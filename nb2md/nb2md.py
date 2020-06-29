import argparse
import json
import subprocess
import sys
import urllib
import urllib.request

import boto3
import nbformat as nbf

try:
    from nb2md.version import __version__
except ImportError:
    from version import __version__


def local(args):
    if type(args) == list:
        cmd = ' '.join(args)
    else:
        cmd = args

    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as grepexc:
        fatal("Error ({}): {}".format(grepexc.returncode, grepexc.output))
    print(out)


def fatal(msg):
    """
    Print message error and terminate execution
    :param msg: message error
    :return:
    """
    print("{}; exiting.".format(msg))
    sys.exit(0)


def read_s3(uri):
    """
    Read notebook from S3
    :param s3uri: S3 URI
    :return: contents of file
    """
    parts = urllib.parse.urlsplit(uri)
    bucket = parts.netloc
    key = parts.path[1:]

    print("Reading input file from S3: bucket={} key={}".format(bucket, key))

    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)

    return obj.get()['Body'].read().decode('utf-8')


def read_http(uri):
    """
    Read notebook from HTTP URI
    :param uri: HTTP URI, e.g., "http://...."
    :return:
    """

    return urllib.request.urlopen(uri).read()


class Notebook:
    """
    This class takes care of:
    1. parsing notebooks from Zeppelin and Jupyter formats
    2. dumoing the notebook to Markdown format
    """

    def read(self, pathname):
        """
        Read pathname (can be either local file or S3 URI)
        :param pathname: pathname of notebook
        :return: contents of file
        """
        if pathname.startswith("s3://"):
            return read_s3(pathname)
        elif pathname.startswith("http://") or pathname.startswith("https://"):
            return read_http(pathname)
        else:
            return open(pathname, "r").read().encode("utf-8")

    def load(self, pathname):
        """
        Parse notebook
        :param pathname: pathname of notebook
        :return:
        """

        if pathname.endswith(".json"):
            self.parseZeppelin(pathname)
        elif pathname.endswith(".ipynb"):
            self.parseJupyter(pathname)

    def parseJupyter(self, pathname):
        """
        Parse notebook as Jupyter notebook
        :param pathname: notebook pathname
        :return:
        """

        print("Parsing Jupyter notebook from {} ...".format(pathname))

        # remember type of notebook
        self.format = "jupyter"
        self.data = []
        self.nb = nbf.read(pathname, as_version=4)

        print("Notebook number of cells: {}".format(len(self.nb.cells)))

    def parseZeppelin(self, pathname):
        """
        Parse notebook as Zeppelin notebook
        :param pathname: notebook pathname
        :return:
        """

        print("Parsing Zeppelin notebook from {} ...".format(pathname))

        # remember type of notebook
        self.format = "zeppelin"

        # parse notebook contents to data structure
        self.data = json.loads(self.read(pathname))

        # initialise new Jupyter notebook
        self.nb = nbf.v4.new_notebook()
        self.nb['cells'] = []

        print("Notebook name: {}".format(self.data['name']))
        print("Notebook number of paragraphs: {}".format(len(self.data['paragraphs'])))

        # number of cells containing markdown
        count_cells_md = 0

        # number of cells containing code
        count_cells_code = 0

        # number of exeuction blocks in code cells
        execution_count = 0

        for paragraph in self.data["paragraphs"]:

            source = paragraph.get('text')

            if not source:
                continue

            elif source.startswith("%md"):
                count_cells_md += 1
                cell = nbf.v4.new_markdown_cell(source[3:].strip())
                self.nb['cells'].append(cell)

            elif not source.startswith("%") or \
                    source.startswith("%sh") or \
                    source.startswith("%spark.dep") or \
                    source.startswith("%pyspark") or \
                    source.startswith("%spark") or \
                    source.startswith("%sql"):
                count_cells_code += 1
                execution_count += 1
                outputs = []

                results = paragraph.get("results", {})
                msgs = results.get("msg", [])
                for msg in msgs:
                    if msg["type"] == "TEXT":
                        outputs.append(nbf.v4.new_output("execute_result", {'text/plain': [msg["data"]]},
                                                         execution_count=execution_count))
                    elif msg["type"] == "TABLE":
                        outputs.append(nbf.v4.new_output("execute_result", {'text/plain': [msg["data"]]},
                                                         execution_count=execution_count))
                    elif msg["type"] == "HTML":
                        outputs.append(nbf.v4.new_output("execute_result", {'text/html': [msg["data"]]},
                                                         execution_count=execution_count))

                    else:
                        print("Warning: unsupported output type: '{}'".format(msg["type"]))
                        print(msg)

                cell = nbf.v4.new_code_cell(source=source, execution_count=execution_count, outputs=outputs)
                self.nb['cells'].append(cell)

            else:
                print("Warning: unsupported paragraph type: '{}...'".format(paragraph["text"][:10].strip()))

        print("Found {} Markdown cells and {} code cells".format(count_cells_md, count_cells_code))

    def save(self, pathname):
        """
        Save loaded notebook
        :param pathname: save to pathname, guessing format
        :return:
        """

        if pathname.endswith(".ipynb"):
            return self.saveJupyter(pathname)
        elif pathname.endswith(".md") or pathname == "auto":
            return self.saveMarkdown(pathname)
        else:
            fatal("Unknown output format: {}".format(pathname))

    def saveJupyter(self, pathname):
        """
        Save as Jupyter notebook
        :param pathname:
        :return:
        """

        if pathname == "auto":
            if "name" in self.data:
                # try to use guessed notebook name to form destination pathname
                pathname = "{}.ipynb".format(self.data["name"])
                print("Using notebook name as Jupyter notebook base pathname: {}".format(pathname))
            else:
                fatal("automatic destination pathname not supported for Jupyter notebooks")

        print("Saving notebook to {} ...".format(pathname))

        with open(pathname, 'w') as f:
            nbf.write(self.nb, f)

        return pathname

    def saveMarkdown(self, pathname):
        """
        Save as Markdown notebook
        :param pathname:
        :return:
        """

        if pathname == "auto":
            if "name" in self.data:
                # try to use guessed notebook name to form destination pathname
                pathname = "{}.nb.md".format(self.data["name"])
                print("Using notebook name as Markdown notebook base pathname: {}".format(pathname))
            else:
                fatal("automatic destination pathname not supported for Jupyter notebooks")

        print("Saving notebook to {} ...".format(pathname))

        with open(pathname, 'w') as f:

            cell_count = 0
            for cell in self.nb.cells:
                if cell.cell_type == "markdown":
                    f.write(cell.source)
                elif cell.cell_type == "code":
                    cell_count += 1

                    if cell.source.startswith("///"):
                        title = ": {}".format(cell.source.splitlines()[0][3:].strip().capitalize())
                    else:
                        title = ""

                    f.write("\n\n---\n\n### [#{}]{}\n\n".format(cell_count, title))
                    f.write("\n```\n")
                    f.write(cell.source)
                    f.write("\n```\n")

                    if cell.outputs:
                        f.write("Output:\n")
                    for output in cell.outputs:
                        if output["output_type"] == "execute_result":
                            f.write("\n```\n")
                            for elem in output.data['text/plain']:
                                f.write(str(elem))
                            f.write("\n```\n")

        return pathname


def main():
    """
    Main function
    :return:
    """
    long_name = 'nb2md v{} on Python v{}.{}.{}'.format(__version__, *sys.version_info[:3])

    parser = argparse.ArgumentParser(description=long_name)
    parser.add_argument('--src', help="path of source pathname (local or S3)")
    parser.add_argument('--dst', default="auto", help="path of destination pathname")
    parser.add_argument('--push', help="commit and push changes to repository")

    if len(sys.argv) == 1:
        # print help and exit.
        parser.print_help()
        print()
        sys.exit(1)

    # parse params
    args = parser.parse_args()

    if not args.src:
        fatal("Required input pathname is required")

    nb = Notebook()
    nb.load(args.src)
    pathname = nb.save(args.dst)

    if args.push:
        msg = input("Commit message: ")
        print("Adding, committing and pushing to repository ...")
        local("git add {}".format(pathname))
        local("git commit -m '{}' && git push".format(msg))

    print("Operation completed.")


if __name__ == "__main__":
    main()
