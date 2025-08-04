# CSS编码规范

**CSS代码规范 | CSS编程标准 | CSS最佳实践 | CSS代码审查**

CSS样式表语言的编码规范和最佳实践指南，适用于代码审查和质量控制。

---

## 1. 基本原则

- 使用BEM命名方法论
- 保持代码简洁和可维护
- 优先使用类选择器
- 避免过度嵌套
- 注重代码复用

## 2. 命名规范

### BEM命名方法论
**原则**：块、元素、修饰符的组合创建清晰类名结构

**块（Block）**：独立组件，如header、menu、button
**元素（Element）**：块的一部分，如header__title、menu__item
**修饰符（Modifier）**：改变外观或行为，如button--primary、menu__item--active

### 通用命名规则
**格式规范**：
- 使用小写字母
- 使用连字符（-）连接单词
- 使用双下划线（__）表示元素关系
- 使用双连字符（--）表示修饰符

## 3. 代码组织

**属性排序**：按逻辑顺序组织CSS属性

**属性分组**：
- 定位：position、top、right、bottom、left、z-index
- 盒模型：display、float、width、height、margin、padding、border
- 排版：font、line-height、text-align、word-wrap
- 视觉效果：background、color、opacity、box-shadow
- 其他：cursor、overflow、transition

## 4. 响应式设计

**移动优先**：先为移动设备编写样式，再用媒体查询为大屏幕添加样式
**相对单位**：优先使用rem、em、vw、vh而不是固定像素
**断点设置**：设置合理断点，如768px（平板）、1024px（桌面）
**布局适配**：使用百分比、flexbox或grid布局

## 5. 性能优化

**文件优化**：
- 避免@import，使用link标签
- 合并和压缩CSS文件
- 使用CSS Sprites减少图片请求
- 移除未使用的CSS代码

**选择器优化**：
- 避免复杂选择器
- 优先使用类选择器
- 避免通配符选择器
- 减少嵌套层级

**动画优化**：
- 优先使用CSS3动画
- 使用transform和opacity
- 避免影响页面布局
- 使用will-change优化性能

## 6. 浏览器兼容性

**前缀处理**：使用Autoprefixer自动处理浏览器前缀
**浏览器测试**：测试主流浏览器兼容性
**优雅降级**：为不支持新特性的浏览器提供基础样式
**样式重置**：使用normalize.css确保一致基础样式

## 7. CSS变量使用

**变量定义**：在:root中定义可复用值，如颜色、字体、间距
**变量命名**：使用kebab-case，以--开头，如--primary-color
**变量使用**：使用var()函数引用变量
**变量作用域**：遵循CSS级联规则，可重新定义