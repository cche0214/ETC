# 交互式查询功能使用指南

## 功能概述

交互式查询页面提供两种检索方式：
1. **传统检索** - 类似CNKI的高级检索，支持多条件组合查询
2. **AI智能检索** - 基于自然语言的智能检索，支持对话式查询

## 页面路由

- 访问路径: `/search`
- 从首页导航: 点击顶部"交互式查询"链接

## 1. 传统检索

### 功能特点
- 支持多字段组合检索（主题、作者、文献来源等）
- 支持精确/模糊匹配
- 支持文献类型筛选
- 支持时间范围限制
- 支持逻辑运算符（AND、OR、NOT）

### 检索字段

#### 基础字段
- **主题**: 文献的主题关键词
- **作者**: 作者姓名
- **文献来源**: 期刊名称、会议名称等

#### 匹配方式
- **精确**: 完全匹配检索词
- **模糊**: 包含检索词即可

#### 文献类型
- OA期刊
- 网络首发
- 博览出版
- 中文文摘
- 同义词扩展

#### 时间范围
- 发表时间
- 更新时间
- 支持自定义日期范围
- 快捷选项：近1年、近3年、近5年

### 使用示例

```javascript
// 检索ETC相关的最近3年文献
{
  subject: 'ETC系统',
  subjectMatch: 'fuzzy',
  author: '',
  source: '',
  docTypes: ['学术期刊'],
  timeType: 'publish',
  timeLimit: '3years'
}
```

### 检索结果

显示信息：
- 文献标题
- 作者信息
- 来源期刊
- 发表时间
- 摘要
- 操作按钮（查看详情、引用、下载）

排序方式：
- 相关度排序
- 时间排序
- 引用量排序

## 2. AI智能检索

### 功能特点
- 自然语言输入
- 智能理解查询意图
- 相关度评分
- AI解读文献
- 推荐相关文献

### 检索模式

#### 快速模式
- 快速返回结果
- 适合简单查询
- 响应时间：1-2秒

#### 段落模式
- 段落级精准匹配
- 适合查找特定内容
- 响应时间：2-3秒

#### 高效模式
- 平衡精度和速度
- 适合一般查询
- 响应时间：1.5-2.5秒

#### 专业模式
- 深度语义分析
- 适合专业研究
- 响应时间：3-5秒

### 使用方法

#### 输入方式
1. **键盘输入**: 直接在搜索框输入问题
2. **语音输入**: 点击麦克风图标进行语音输入
3. **快捷键**: 
   - `Enter`: 发送查询
   - `Shift+Enter`: 换行

#### 查询示例

**简短描述**
```
清华大学发表关于人工智能的文献
```

**多个关键词**
```
我国古代 粮食 仲裁
```

**问题描述**
```
ETC大数据分析与应用研究有哪些最新进展？
```

**复杂查询**
```
近三年关于基于深度学习的交通流量预测的博士论文
```

### 文献筛选

支持的文献类型：
- 全部
- 学术期刊
- 博士论文
- 硕士论文
- 国内会议
- 国际会议
- 报纸
- 特色期刊
- 学术辑刊
- 国家标准
- 行业标准
- 成果

高级筛选：
- 仅有全文
- 包含资讯
- 包含非中文文献

### AI检索结果

每条结果包含：
- 文献标题
- 文献类型标签
- 作者和发表时间
- AI生成的摘要
- 相关度评分（0-100%）
- 操作按钮：
  - 查看全文
  - AI解读
  - 相关文献

## 数据接口对接

### API文件位置
`src/api/search.js`

### 主要接口

#### 传统检索
```javascript
import { traditionalSearch } from '@/api/search'

const results = await traditionalSearch({
  subject: 'ETC',
  author: '',
  source: '',
  docTypes: ['学术期刊'],
  timeLimit: '3years'
})
```

#### AI智能检索
```javascript
import { aiSearch } from '@/api/search'

const results = await aiSearch({
  query: '人工智能在交通领域的应用',
  mode: 'fast',
  filters: ['学术期刊', '博士'],
  options: {
    onlyFullText: true
  }
})
```

#### 获取搜索建议
```javascript
import { getSearchSuggestions } from '@/api/search'

const suggestions = await getSearchSuggestions('ETC')
```

#### 文献详情
```javascript
import { getDocumentDetail } from '@/api/search'

const detail = await getDocumentDetail(documentId)
```

#### 导出结果
```javascript
import { exportResults } from '@/api/search'

await exportResults([id1, id2, id3], 'pdf')
```

## 数据格式规范

### 传统检索请求
```javascript
{
  subject: string,          // 主题
  subjectMatch: 'exact' | 'fuzzy',  // 匹配方式
  author: string,           // 作者
  authorMatch: 'exact' | 'fuzzy',
  source: string,           // 来源
  sourceMatch: 'exact' | 'fuzzy',
  docTypes: string[],       // 文献类型
  timeType: 'publish' | 'update',  // 时间类型
  startDate: string,        // 开始日期
  endDate: string,          // 结束日期
  timeLimit: '1year' | '3years' | '5years' | ''
}
```

### 传统检索响应
```javascript
{
  total: number,            // 总数
  data: [{
    title: string,          // 标题
    author: string,         // 作者
    source: string,         // 来源
    date: string,           // 日期
    abstract: string,       // 摘要
    keywords: string[],     // 关键词
    citations: number,      // 引用数
    downloads: number       // 下载数
  }]
}
```

### AI检索请求
```javascript
{
  query: string,            // 查询语句
  mode: 'fast' | 'paragraph' | 'efficient' | 'professional',
  filters: string[],        // 文献类型过滤
  options: {
    onlyFullText: boolean,
    includeNews: boolean,
    includeNonChinese: boolean
  }
}
```

### AI检索响应
```javascript
{
  total: number,
  data: [{
    title: string,
    type: string,           // 文献类型
    author: string,
    institution: string,    // 机构
    date: string,
    summary: string,        // AI生成的摘要
    relevance: number,      // 相关度 0-100
    citations: number,
    keywords: string[],
    fullText: boolean       // 是否有全文
  }]
}
```

## 样式定制

### 主题色
- 主色: `#4A9EFF`
- 辅助色: `#00D4FF`
- 强调色: `#FF6B00`

### 关键类名
- `.search-query-page` - 页面容器
- `.traditional-search` - 传统检索面板
- `.ai-search` - AI检索面板
- `.search-results` - 检索结果列表
- `.result-item` - 单个结果项

## 后续扩展建议

1. **搜索历史**: 记录用户搜索历史
2. **收藏功能**: 收藏感兴趣的文献
3. **批量操作**: 批量导出、批量下载
4. **文献对比**: 对比多篇文献
5. **引文网络**: 可视化引用关系
6. **智能推荐**: 基于搜索历史推荐相关文献
7. **协同过滤**: 根据其他用户行为推荐
8. **知识图谱**: 构建领域知识图谱

## 性能优化

1. **防抖处理**: 搜索输入防抖，减少API调用
2. **结果缓存**: 缓存检索结果，避免重复请求
3. **分页加载**: 大量结果分页显示
4. **虚拟滚动**: 长列表使用虚拟滚动
5. **懒加载**: 图片和详情内容懒加载

## 浏览器兼容性

- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

## 常见问题

### Q: 如何添加新的检索字段？
A: 在 `searchForm` 中添加新字段，在表单中添加对应的输入控件。

### Q: 如何修改AI模式？
A: 修改 `aiModes` 数组，添加或删除模式选项。

### Q: 如何自定义文献类型？
A: 修改 `aiFilters` 数组中的选项。

### Q: 检索结果如何排序？
A: 传统检索支持相关度、时间、引用量排序。AI检索默认按相关度排序。

## 技术栈

- Vue 3 - 前端框架
- Vue Router - 路由管理
- Axios - HTTP请求
- CSS3 - 样式实现
