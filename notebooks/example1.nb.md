# An example of dataframe creation

---

### [#1]


```
import spark.implicits._
```
Output:

```
import spark.implicits._

```


---

### [#2]


```
val df = Seq((8, "bat"),(64, "mouse"),(-27, "horse")).toDF("number", "word")

```
Output:

```
df: org.apache.spark.sql.DataFrame = [number: int, word: string]

```


---

### [#3]


```
df.show()
```
Output:

```
+------+-----+
|number| word|
+------+-----+
|     8|  bat|
|    64|mouse|
|   -27|horse|
+------+-----+


```
