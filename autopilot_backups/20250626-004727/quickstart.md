# AI 核心增强系统快速入门

本指南将帮助您快速上手 AI 核心增强系统，通过简单的步骤了解系统的基本使用方法。

## 1. 安装

### 使用 npm 安装

```bash
npm install ai-core-enhancement
```

### 使用 yarn 安装

```bash
yarn add ai-core-enhancement
```

## 2. 基本使用

### 2.1 创建系统实例

```javascript
// 导入核心模块
const { AIEnhancementCore } = require('ai-core-enhancement');

// 创建系统实例
const aiCore = new AIEnhancementCore();

// 初始化系统
await aiCore.initialize();
```

### 2.2 使用内置工具

```javascript
// 执行文件读取工具
const readResult = await aiCore.executeTool('read_file', {
  path: './data.json',
  encoding: 'utf8'
});

console.log('文件内容:', readResult.data.content);

// 执行命令行工具
const cmdResult = await aiCore.executeTool('execute_command', {
  command: 'echo "Hello, World!"',
  timeout: 5000
});

console.log('命令输出:', cmdResult.data.stdout);
```

### 2.3 使用缓存系统

```javascript
// 启用缓存
aiCore.config.cache.enabled = true;

// 第一次调用 - 执行实际操作
const result1 = await aiCore.executeTool('expensive_operation', {
  data: 'input'
});

// 第二次调用 - 从缓存获取结果
const result2 = await aiCore.executeTool('expensive_operation', {
  data: 'input'
});

// 清除特定工具的缓存
aiCore.cacheManager.invalidate('expensive_operation');
```

## 3. 自定义配置

### 3.1 基本配置

```javascript
const config = {
  // 上下文配置
  context: {
    maxHistorySize: 100,
    persistenceEnabled: true,
    persistencePath: './context-store'
  },
  
  // 缓存配置
  cache: {
    enabled: true,
    maxSize: 1000,
    ttl: 3600, // 秒
    persistenceEnabled: true
  },
  
  // 错误处理配置
  errorHandling: {
    retryEnabled: true,
    maxRetries: 3,
    retryDelay: 1000
  }
};

const aiCore = new AIEnhancementCore(config);
```

### 3.2 高级配置

```javascript
const advancedConfig = {
  // 基本配置
  ...config,
  
  // 性能监控配置
  performance: {
    enabled: true,
    sampleInterval: 1000,
    detailedMetrics: true,
    alertThresholds: {
      cpuUsage: 80,
      memoryUsage: 70,
      responseTime: 2000
    }
  },
  
  // 日志配置
  logging: {
    level: 'info',
    format: 'json',
    destination: './logs/system.log',
    rotation: {
      enabled: true,
      maxSize: '10m',
      maxFiles: 5
    }
  }
};
```

## 4. 注册自定义工具

### 4.1 创建工具类

```javascript
const { Tool } = require('ai-core-enhancement');

class CustomTool extends Tool {
  constructor() {
    super({
      id: 'custom_tool',
      name: '自定义工具',
      description: '这是一个自定义工具示例',
      version: '1.0.0',
      category: 'custom'
    });
    
    this.paramSchema = {
      properties: {
        input: {
          type: 'string',
          description: '输入数据',
          minLength: 1
        },
        options: {
          type: 'object',
          description: '可选配置'
        }
      },
      required: ['input']
    };
  }
  
  async execute(params) {
    try {
      // 工具实现逻辑
      const result = `处理结果: ${params.input.toUpperCase()}`;
      
      return {
        success: true,
        data: {
          result,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: `执行失败: ${error.message}`
      };
    }
  }
}
```

### 4.2 注册工具

```javascript
// 创建工具实例
const customTool = new CustomTool();

// 注册工具
aiCore.toolRegistry.registerTool(customTool, 'custom_provider');

// 使用自定义工具
const result = await aiCore.executeTool('custom_tool', {
  input: 'hello world',
  options: {
    format: 'text'
  }
});

console.log(result.data.result); // 输出: 处理结果: HELLO WORLD
```

## 5. 使用插件系统

### 5.1 创建插件

```javascript
const { Plugin } = require('ai-core-enhancement');

class ExamplePlugin extends Plugin {
  constructor() {
    super({
      id: 'example_plugin',
      name: '示例插件',
      version: '1.0.0',
      dependencies: []
    });
  }
  
  async initialize(core) {
    // 存储核心实例引用
    this.core = core;
    
    // 注册插件提供的工具
    this.registerTools();
    
    // 添加事件监听器
    this.registerEventListeners();
    
    console.log('示例插件已初始化');
    return true;
  }
  
  registerTools() {
    // 创建并注册工具
    const myTool = new CustomTool();
    this.core.toolRegistry.registerTool(myTool, this.id);
  }
  
  registerEventListeners() {
    // 监听系统事件
    this.core.events.on('tool:executed', (data) => {
      console.log(`工具执行: ${data.toolId}, 结果: ${data.success ? '成功' : '失败'}`);
    });
  }
  
  async destroy() {
    // 清理资源
    console.log('示例插件已销毁');
    return true;
  }
}
```

### 5.2 注册插件

```javascript
// 创建插件实例
const examplePlugin = new ExamplePlugin();

// 注册插件
await aiCore.pluginManager.registerPlugin(examplePlugin);

// 启用插件
await aiCore.pluginManager.enablePlugin('example_plugin');
```

## 6. 错误处理

```javascript
try {
  const result = await aiCore.executeTool('risky_tool', {
    param: 'value'
  });
  
  if (!result.success) {
    console.error('工具执行失败:', result.error);
    // 处理错误...
  }
} catch (error) {
  console.error('系统错误:', error.message);
  // 处理系统级错误...
}
```

## 7. 事件监听

```javascript
// 监听工具执行事件
aiCore.events.on('tool:executed', (data) => {
  console.log(`工具 ${data.toolId} 执行完成，耗时: ${data.metadata.executionTime}ms`);
});

// 监听错误事件
aiCore.events.on('error', (error) => {
  console.error('系统错误:', error.message);
});

// 监听缓存事件
aiCore.events.on('cache:hit', (data) => {
  console.log(`缓存命中: ${data.key}`);
});
```

## 8. 后续步骤

- 查看[增强模块详解](../../guidelines/enhancement_module.md)了解核心模块的实现细节
- 了解[工具集成技术](../../guidelines/tool_integration.md)的技术实现
- 探索[常见使用场景](./common_scenarios.md)中的更多示例

## 9. 故障排除

### 常见问题

1. **初始化失败**
   - 检查配置参数是否正确
   - 确认依赖项已正确安装

2. **工具执行错误**
   - 验证工具参数是否符合要求
   - 检查工具是否已正确注册

3. **性能问题**
   - 检查缓存配置是否合理
   - 调整性能监控参数

### 获取帮助

如果您遇到无法解决的问题，请参考以下资源：

- 查看详细的[API文档](../api/core_api.md)
- 在[GitHub Issues](https://github.com/example/ai-core-enhancement/issues)提交问题
- 加入[社区论坛](https://forum.example.com)寻求帮助