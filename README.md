# Kromium
### Interpreted statically-typed programming langauge

![kromium-cover-png](https://github.com/user-attachments/assets/2067e776-a0ac-4f0c-b352-85b937979e56)

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
- Importing built-in libraries and custom files
- Comments 


### How to use Kromium

To execute a program, run *__main__.py* and use the built-in function **run("path/to/file.kr")**



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
**Variables can be unfinished by using a ;**

```c
new const string name = "Bob"
new const int age = 22
new const double gpa;
new const list grades = ["A", "B" , "D", "B"]

name += " Ross" ~Throws an error~

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
|-------------------|-------------|
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

#### Importing 

To import a built in library, use *include* keyword followed by a string with a *#* in it's beggining

```ruby
include "#Math.kr"
```

Current libraries:
- Math: abs, add, cos, div, fact, floor, log2, mul, roof, round, sin, sqrt, sub
- String (*coming soon!*)
- KrTools (*coming soon!*)
- Kraphics (*maybe*)

To import a .kr file, use *include* keyword followed by a string containing a path to file

```ruby
include "path/to/file.kr"
```

#### Comments

Syntax: ```~something~```

```ruby

~This is how you write a comment~

```