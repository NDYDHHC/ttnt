# Agent Development Guidelines / AI 辅助开发规范

在使用 AI/Agent 进行本项目的代码生成和重构时，请严格遵守以下架构和编程原则：

## 1. 数据与逻辑分离 (Thin Classes)
- **类尽量只有定义**：类（Class/Struct）应主要用于数据结构的定义（类似于 POD / Plain Old Data）。
- 避免在类内部编写复杂的业务逻辑、状态变更方法和重量级的成员函数。

## 2. 核心操作提取 (Utility-Driven)
- **将操作抽取至 Utils**：针对类中数据的修改、计算和处理等所有的操作，都应放到专门的 `Utils` 文件中（例如 `MeshUtils.h` / `MeshUtils.cpp`）。
- 通过将对象作为参数传递给 Util 函数来进行操作。

## 3. 函数式编程原则 (Functional Programming)
- **纯函数 (Pure Functions)**：函数的实现应尽可能符合函数式编程原则，确保相同的输入始终产生相同的输出。
- **避免副作用 (No Side Effects)**：尽量不要在函数内部修改全局变量或外部状态，优先返回全新的结果数据结构，或者清晰地限定输入输出引用。
- **不可变性 (Immutability)**：尽可能保护输入参数不被随意更改，大量使用 `const` 引用传递。