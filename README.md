# Kromium
### Interpreted statically-typed programming langauge

![kromium-cover](https://github.com/user-attachments/assets/b14fde76-d28e-4ba0-b6b8-e7c792ed863a)

### Kromium features
- Basic data types : integer, double, string, list, func
- Unary operations
- Binary operations
- Stronglly-typed variables
- If/elif/else expressions
- for and while loops
- functions and built-in functions
- multi-line statments
- file support (*coming soon!*)


### How to use Kromium

You'll need: `git` and `python` (v3.9 or above)

**To open console, run "kromiumlang.exe"**

### Syntax

#### Datatypes

| Data type | Example     | Keyword |
|-----------|-------------|---------|
| String    | "abc", "ww" | string  |
| Integer   | 1, 5, 6     | int     |
| Double    | 1.3, 4.55   | double  |
| List      | [1 , "def"] | list    |
| Function  | <function a>| func    |


Variable Declaration
```py
new string name = "Bob"
new int age = 22
new double gpa = 3.7
new list grades = ["A", "B" , "D", "B"]

name += " Ross"
age += 1 ...

```

***$ = new line***

Function declaration

```py

func add(a , b) -> a + b
func sub(c , d) { out(c) $ out(d) $ out(c - d)} 
add(3 , 4)
new func subtract = sub

```

#### Built-ins
Built-in functions:
- out - prints something to console
- input - returns the user input
- typeof - returns the string of given type (If type of arg is String, function return "str")
- integer - returns the argument is integer (If possible)
- len - returns the lenght of stringed argument


#### For & While loops

```py 
new int i = 0
for i; i < 5; i += 1 {
    out(i ^ 2)
}

```

```py 
new int i = 0
while i < 10 {
    i += 1
    out(i * 2)
}

```


#### Operators

|     Name          |      Op     |
|---------------    |-------------|
| addition          | +           |
| subtaction        | -           | 
| multiplication    | *           |
| division          | /           |
| lte               | <=          |
| gte               | >=          |
| lt                | <           |
| gt                | >           |
| equals            | =           |
| double-equals     | ==          |
| power             | ** or ^     |
| and               | '&' or 'and'|
| or                | '|' or 'or' |
