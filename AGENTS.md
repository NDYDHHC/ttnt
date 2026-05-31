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

## 4. 命名规范 (Naming Conventions)
以下命名规则遵循 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html#Naming)，适用于类、函数、文件及所有新增代码。

### 4.1 文件命名 (File Names)
- **文件名全部小写，以下划线分隔**（snake_case）：
  - `my_useful_class.h` / `my_useful_class.cpp`
  - `mesh_utils.h` / `mesh_utils.cpp`
- **头文件使用 `.h` 后缀，源文件使用 `.cpp` 后缀**。
- **不要使用 `-`（连字符）作为文件名的一部分**。
- **文件名应具有描述性**，清楚表明其中包含的类或功能。
- **测试文件**以 `_test.cpp` 结尾，如 `mesh_utils_test.cpp`。

### 4.2 类与结构体命名 (Type Names)
- **类、结构体、类型别名（using/typedef）、枚举类型、模板参数类型均使用 PascalCase**（大驼峰，首字母大写，无下划线分隔）：
  - `class MeshData`
  - `class RenderPipelineManager`
  - `struct VertexAttribute`
  - `enum class RenderPassType`
  - `template <typename ElementType>`
- 避免使用常见缩写，除非该缩写比全称更广为人知。

### 4.3 函数命名 (Function Names)
- **普通函数使用 PascalCase**（大驼峰，首字母大写）：
  - `AddTableEntry()`
  - `DeleteUrl()`
  - `OpenFileOrDie()`
  - `ComputeBoundingVolume()`
- **取值（getter）和设值（setter）函数**可使用 snake_case，与小写成员变量名对应：
  - `int count() const;`
  - `void set_count(int count);`
- **Utils 文件中的纯函数同样使用 PascalCase**，如 `MeshUtils::TransformVertices()`。

### 4.4 变量命名 (Variable Names)
- **普通局部变量、函数参数**使用 snake_case：
  - `table_name`
  - `vertex_count`
  - `input_buffer`
- **类成员变量**在 snake_case 后加**尾部下划线** `_`：
  - `class MyClass { int table_name_; std::string display_text_; };`
- **结构体成员变量**使用 snake_case，**不加尾部下划线**（与普通变量一致）：
  - `struct VertexData { float position_x; float position_y; };`
- **全局变量**禁止使用。如需全局状态，请使用单例或命名空间作用域的函数。

### 4.5 常量命名 (Constant Names)
- **编译期常量、`constexpr`、`const` 全局/静态变量**以 `k` 开头，后接 PascalCase：
  - `constexpr int kDaysInAWeek = 7;`
  - `const float kDefaultMargin = 4.0f;`
- **枚举值**与常量命名一致，以 `k` 开头：
  - `enum class ColorSpace { kSrgb, kLinear, kRaw };`

### 4.6 宏命名 (Macro Names)
- **宏全部大写，以下划线分隔**：
  - `#define MY_MACRO(x) ...`
  - `#define PI_OVER_TWO 1.570796f`
- 尽量避免定义宏；优先使用 `constexpr` 或内联函数。

### 4.7 命名空间命名 (Namespace Names)
- **命名空间全部小写，以下划线分隔**：
  - `namespace tt { ... }`
  - `namespace mesh_processing { ... }`
- **顶层命名空间应为项目名或组织名**，本项目使用 `tt`。
- 避免嵌套过深（建议不超过 2 层）。

### 4.8 新功能/模块命名指南 (Feature & Module Naming)
当添加新的功能模块时，请遵循以下文件组织与命名约定：

- **一个功能模块对应一个目录**，目录名使用 snake_case，如 `mesh_processing/`、`level_importer/`。
- 目录下应包含：
  - 数据结构定义：`xxx_data.h` / `xxx_data.cpp`（类定义）
  - 操作工具函数：`xxx_utils.h` / `xxx_utils.cpp`（纯函数集合）
  - 功能入口/对外接口：`xxx_module.h` / `xxx_module.cpp`
  - 单元测试：`xxx_test.cpp`
- **示例**：新增 `碰撞检测` 功能：
  ```
  collision_detection/
    collision_data.h          // CollisionData, CollisionResult 等数据类
    collision_data.cpp
    collision_utils.h         // DetectCollision(), ComputeAABB() 等纯函数
    collision_utils.cpp
    collision_module.h        // 外部调用入口
    collision_module.cpp
    collision_test.cpp        // 单元测试
  ```
- **名称应自解释**：目录名、文件名、类名要做到见名知意，无需额外注释即可理解其用途。