# Kromium
### Interpreted statically-typed programming langauge

![kromium-cover-png](https://github.com/user-attachments/assets/b14fde76-d28e-4ba0-b6b8-e7c792ed863a)

### Kromium features
- Basic data types : integer, double, string, list, func
- Unary operations
- Binary operations
- Stronglly-typed variables and constants
- If/elif/else expressions
- For and while loops
- Functions and built-in functions
- Multi-line statments
- File support
- Comments 


### How to use Kromium

To execute a program, open *kromiumlang.exe* and use the built-in function **run("path/to/file.kr")**



### Syntax

#### Datatypes

| Data type | Example       | Keyword |
|-----------|---------------|---------|
| String    | "abc", "ww"   | string  |
| Integer   | 1, 5, 6       | int     |
| Double    | 1.3, 4.55     | double  |
| List      | [1 , "def"]   | list    |
| Function  | &lt;function a&gt;| func    |





Variable Declaration
```c
new string name = "Bob"
new int age = 22
new double gpa = 3.7
new list grades = ["A", "B" , "D", "B"]

name += " Ross"
age += 1 ...

```

**Variables can be constants**

```c
new const string name = "Bob"
new const int age = 22
new const double gpa = 3.7
new const list grades = ["A", "B" , "D", "B"]

name += " Ross" //Throws an error

```

***$ = new line***


#### Functions
Function declaration

```c

func add(a , b) -> a + b
func sub(c , d) { 
    out(c)  
    out(d) 
    return c - d
} 
add(3 , 4)
new func subtract = sub

```

You can use return in functions

#### Built-ins
Built-in functions:
- out - prints something to console
- input - returns the user input
- typeof - returns the string of given type (If type of arg is String, function return "str")
- integer - returns the argument is integer (If possible)
- len - returns the lenght of stringed argument

#### If statments

Syntax : ``` if condition { do something  } elif condition {do something other} else {just do something}```


```c
new int salary = 60000

if salary < 50000 {
    out("You make less then $50000")
}
elif salary > 100000{
    out("You are rich!!!!!!!!")
}
else{
    out("You are an average person")
}

```

#### For & While loops

```c
new int i = 0
for i; i < 5; i += 1 {
    out(i ^ 2)
    if i == 2{
        advance
    }
    if i == 4{
        break
    }
}

```

```c 
new int i = 0
while i < 10 {
    i += 1
    out(i * 2)
    if i == 2{
        advance
    }
    if i == 4{
        break
    }
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
| not-equals        | !=          |
| power             | ** or ^     |
| and               | '&' or 'and'|
| or                | "\|" or 'or' |
