# 工具集成技术实现

本文档详细说明AI系统的工具集成技术实现，包括工具接口设计、调用机制和扩展方法。

## 3.1 工具集成架构

### 核心组件
- **工具注册表**：管理所有可用工具，提供注册和查询功能
- **工具提供者**：实现具体工具功能的组件，遵循统一接口
- **参数验证器**：验证工具调用参数的有效性和安全性
- **结果处理器**：处理工具执行结果，包括格式化和错误处理
- **权限管理器**：控制工具的访问权限和使用限制

### 系统架构
- **插件化设计**：工具以插件形式集成，支持动态加载和卸载
- **统一接口**：所有工具遵循统一的接口规范，确保一致性
- **可扩展性**：支持自定义工具的开发和集成
- **版本管理**：支持工具的版本控制和兼容性检查

## 3.2 工具接口设计

### 基础工具接口
```typescript
/**
 * 工具接口 - 所有工具必须实现的基础接口
 */
interface Tool {
  /**
   * 工具唯一标识符
   */
  readonly id: string;
  
  /**
   * 工具名称
   */
  readonly name: string;
  
  /**
   * 工具描述
   */
  readonly description: string;
  
  /**
   * 工具版本
   */
  readonly version: string;
  
  /**
   * 参数模式定义
   */
  readonly paramSchema: ParamSchema;
  
  /**
   * 执行工具
   * @param params 工具参数
   * @returns 执行结果
   */
  execute(params: Record<string, any>): Promise<ToolResult>;
  
  /**
   * 验证参数
   * @param params 待验证的参数
   * @returns 验证结果，如果有错误则包含错误信息
   */
  validateParams(params: Record<string, any>): ValidationResult;
}

/**
 * 参数模式定义
 */
interface ParamSchema {
  /**
   * 参数定义
   */
  properties: Record<string, ParamDefinition>;
  
  /**
   * 必需参数列表
   */
  required: string[];
}

/**
 * 参数定义
 */
interface ParamDefinition {
  /**
   * 参数类型
   */
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  
  /**
   * 参数描述
   */
  description: string;
  
  /**
   * 默认值
   */
  default?: any;
  
  /**
   * 枚举值列表（可选）
   */
  enum?: any[];
  
  /**
   * 最小值（数字类型）
   */
  minimum?: number;
  
  /**
   * 最大值（数字类型）
   */
  maximum?: number;
  
  /**
   * 最小长度（字符串或数组）
   */
  minLength?: number;
  
  /**
   * 最大长度（字符串或数组）
   */
  maxLength?: number;
  
  /**
   * 正则表达式模式（字符串）
   */
  pattern?: string;
}

/**
 * 工具执行结果
 */
interface ToolResult {
  /**
   * 执行是否成功
   */
  success: boolean;
  
  /**
   * 结果数据
   */
  data?: any;
  
  /**
   * 错误信息（如果失败）
   */
  error?: string;
  
  /**
   * 执行元数据
   */
  metadata?: {
    /**
     * 执行时间（毫秒）
     */
    executionTime: number;
    
    /**
     * 资源使用情况
     */
    resourceUsage?: {
      cpu?: number;
      memory?: number;
    };
    
    /**
     * 其他元数据
     */
    [key: string]: any;
  };
}

/**
 * 验证结果
 */
interface ValidationResult {
  /**
   * 是否有效
   */
  valid: boolean;
  
  /**
   * 错误信息（如果无效）
   */
  errors?: ValidationError[];
}

/**
 * 验证错误
 */
interface ValidationError {
  /**
   * 参数名
   */
  param: string;
  
  /**
   * 错误消息
   */
  message: string;
  
  /**
   * 错误代码
   */
  code: string;
}
```

### 工具提供者接口
```typescript
/**
 * 工具提供者接口 - 负责创建和管理工具实例
 */
interface ToolProvider {
  /**
   * 提供者ID
   */
  readonly id: string;
  
  /**
   * 提供者名称
   */
  readonly name: string;
  
  /**
   * 获取此提供者支持的所有工具
   */
  getTools(): Tool[];
  
  /**
   * 获取指定ID的工具
   * @param toolId 工具ID
   */
  getTool(toolId: string): Tool | null;
  
  /**
   * 初始化提供者
   */
  initialize(): Promise<void>;
  
  /**
   * 销毁提供者，释放资源
   */
  destroy(): Promise<void>;
}
```

## 3.3 工具注册表实现

```javascript
/**
 * 工具注册表 - 管理所有可用工具
 */
class ToolRegistry {
  constructor() {
    this.tools = new Map();
    this.providers = new Map();
    this.categories = new Map();
  }
  
  /**
   * 注册工具提供者
   * @param {ToolProvider} provider - 工具提供者
   * @returns {boolean} 是否成功注册
   */
  registerProvider(provider) {
    if (this.providers.has(provider.id)) {
      console.warn(`提供者已存在: ${provider.id}`);
      return false;
    }
    
    this.providers.set(provider.id, provider);
    
    // 注册此提供者的所有工具
    const tools = provider.getTools();
    for (const tool of tools) {
      this.registerTool(tool, provider.id);
    }
    
    return true;
  }
  
  /**
   * 注册单个工具
   * @param {Tool} tool - 工具实例
   * @param {string} providerId - 提供者ID
   * @returns {boolean} 是否成功注册
   */
  registerTool(tool, providerId) {
    const toolKey = `${providerId}:${tool.id}`;
    
    if (this.tools.has(toolKey)) {
      console.warn(`工具已存在: ${toolKey}`);
      return false;
    }
    
    // 注册工具
    this.tools.set(toolKey, {
      tool,
      providerId,
      registeredAt: Date.now()
    });
    
    // 添加到分类
    const category = tool.category || 'uncategorized';
    if (!this.categories.has(category)) {
      this.categories.set(category, new Set());
    }
    this.categories.get(category).add(toolKey);
    
    console.log(`工具注册成功: ${toolKey}`);
    return true;
  }
  
  /**
   * 获取工具
   * @param {string} toolId - 工具ID
   * @param {string} [providerId] - 提供者ID（可选）
   * @returns {Tool|null} 工具实例或null
   */
  getTool(toolId, providerId) {
    if (providerId) {
      // 获取特定提供者的工具
      const toolKey = `${providerId}:${toolId}`;
      const entry = this.tools.get(toolKey);
      return entry ? entry.tool : null;
    } else {
      // 查找任何提供者的匹配工具
      for (const [key, entry] of this.tools.entries()) {
        if (entry.tool.id === toolId) {
          return entry.tool;
        }
      }
      return null;
    }
  }
  
  /**
   * 检查工具是否存在
   * @param {string} toolId - 工具ID
   * @param {string} [providerId] - 提供者ID（可选）
   * @returns {boolean} 工具是否存在
   */
  hasTool(toolId, providerId) {
    return this.getTool(toolId, providerId) !== null;
  }
  
  /**
   * 获取所有工具
   * @returns {Tool[]} 工具列表
   */
  getAllTools() {
    return Array.from(this.tools.values()).map(entry => entry.tool);
  }
  
  /**
   * 获取特定分类的工具
   * @param {string} category - 分类名称
   * @returns {Tool[]} 工具列表
   */
  getToolsByCategory(category) {
    if (!this.categories.has(category)) {
      return [];
    }
    
    const toolKeys = this.categories.get(category);
    return Array.from(toolKeys).map(key => this.tools.get(key).tool);
  }
  
  /**
   * 获取所有分类
   * @returns {string[]} 分类列表
   */
  getCategories() {
    return Array.from(this.categories.keys());
  }
  
  /**
   * 卸载工具
   * @param {string} toolId - 工具ID
   * @param {string} providerId - 提供者ID
   * @returns {boolean} 是否成功卸载
   */
  unregisterTool(toolId, providerId) {
    const toolKey = `${providerId}:${toolId}`;
    
    if (!this.tools.has(toolKey)) {
      return false;
    }
    
    const entry = this.tools.get(toolKey);
    
    // 从分类中移除
    const category = entry.tool.category || 'uncategorized';
    if (this.categories.has(category)) {
      this.categories.get(category).delete(toolKey);
      
      // 如果分类为空，删除分类
      if (this.categories.get(category).size === 0) {
        this.categories.delete(category);
      }
    }
    
    // 移除工具
    this.tools.delete(toolKey);
    
    return true;
  }
  
  /**
   * 卸载提供者及其所有工具
   * @param {string} providerId - 提供者ID
   * @returns {boolean} 是否成功卸载
   */
  unregisterProvider(providerId) {
    if (!this.providers.has(providerId)) {
      return false;
    }
    
    // 卸载所有相关工具
    for (const [toolKey, entry] of this.tools.entries()) {
      if (entry.providerId === providerId) {
        this.unregisterTool(entry.tool.id, providerId);
      }
    }
    
    // 移除提供者
    this.providers.delete(providerId);
    
    return true;
  }
}
```

## 3.4 参数验证实现

```javascript
/**
 * 参数验证器 - 验证工具调用参数
 */
class ParamValidator {
  /**
   * 验证参数
   * @param {Object} params - 参数对象
   * @param {ParamSchema} schema - 参数模式
   * @returns {ValidationResult} 验证结果
   */
  validate(params, schema) {
    const errors = [];
    
    // 检查必需参数
    for (const requiredParam of schema.required) {
      if (params[requiredParam] === undefined) {
        errors.push({
          param: requiredParam,
          message: `缺少必需参数: ${requiredParam}`,
          code: 'MISSING_REQUIRED'
        });
      }
    }
    
    // 验证每个参数
    for (const [paramName, paramValue] of Object.entries(params)) {
      const paramDef = schema.properties[paramName];
      
      // 跳过未定义的参数
      if (!paramDef) {
        errors.push({
          param: paramName,
          message: `未知参数: ${paramName}`,
          code: 'UNKNOWN_PARAM'
        });
        continue;
      }
      
      // 类型检查
      if (!this.checkType(paramValue, paramDef.type)) {
        errors.push({
          param: paramName,
          message: `参数类型错误: ${paramName} 应为 ${paramDef.type}`,
          code: 'TYPE_ERROR'
        });
        continue;
      }
      
      // 根据类型进行特定验证
      const typeErrors = this.validateByType(paramName, paramValue, paramDef);
      errors.push(...typeErrors);
    }
    
    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined
    };
  }
  
  /**
   * 检查值类型
   * @param {any} value - 要检查的值
   * @param {string} type - 期望的类型
   * @returns {boolean} 是否匹配类型
   */
  checkType(value, type) {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      case 'array':
        return Array.isArray(value);
      default:
        return true; // 未知类型默认通过
    }
  }
  
  /**
   * 根据类型验证参数
   * @param {string} paramName - 参数名
   * @param {any} value - 参数值
   * @param {ParamDefinition} paramDef - 参数定义
   * @returns {ValidationError[]} 验证错误列表
   */
  validateByType(paramName, value, paramDef) {
    const errors = [];
    
    switch (paramDef.type) {
      case 'string':
        // 长度检查
        if (paramDef.minLength !== undefined && value.length < paramDef.minLength) {
          errors.push({
            param: paramName,
            message: `${paramName} 长度不能小于 ${paramDef.minLength}`,
            code: 'MIN_LENGTH'
          });
        }
        
        if (paramDef.maxLength !== undefined && value.length > paramDef.maxLength) {
          errors.push({
            param: paramName,
            message: `${paramName} 长度不能大于 ${paramDef.maxLength}`,
            code: 'MAX_LENGTH'
          });
        }
        
        // 模式检查
        if (paramDef.pattern && !new RegExp(paramDef.pattern).test(value)) {
          errors.push({
            param: paramName,
            message: `${paramName} 不匹配要求的模式`,
            code: 'PATTERN_MISMATCH'
          });
        }
        break;
        
      case 'number':
        // 范围检查
        if (paramDef.minimum !== undefined && value < paramDef.minimum) {
          errors.push({
            param: paramName,
            message: `${paramName} 不能小于 ${paramDef.minimum}`,
            code: 'MIN_VALUE'
          });
        }
        
        if (paramDef.maximum !== undefined && value > paramDef.maximum) {
          errors.push({
            param: paramName,
            message: `${paramName} 不能大于 ${paramDef.maximum}`,
            code: 'MAX_VALUE'
          });
        }
        break;
        
      case 'array':
        // 长度检查
        if (paramDef.minLength !== undefined && value.length < paramDef.minLength) {
          errors.push({
            param: paramName,
            message: `${paramName} 数组长度不能小于 ${paramDef.minLength}`,
            code: 'MIN_ITEMS'
          });
        }
        
        if (paramDef.maxLength !== undefined && value.length > paramDef.maxLength) {
          errors.push({
            param: paramName,
            message: `${paramName} 数组长度不能大于 ${paramDef.maxLength}`,
            code: 'MAX_ITEMS'
          });
        }
        break;
    }
    
    // 枚举值检查
    if (paramDef.enum && !paramDef.enum.includes(value)) {
      errors.push({
        param: paramName,
        message: `${paramName} 必须是以下值之一: ${paramDef.enum.join(', ')}`,
        code: 'ENUM_MISMATCH'
      });
    }
    
    return errors;
  }
}
```

## 3.5 工具执行引擎

```javascript
/**
 * 工具执行引擎 - 处理工具调用和执行
 */
class ToolExecutionEngine {
  /**
   * 构造函数
   * @param {ToolRegistry} toolRegistry - 工具注册表
   */
  constructor(toolRegistry) {
    this.toolRegistry = toolRegistry;
    this.validator = new ParamValidator();
    this.executionHistory = [];
    this.maxHistorySize = 1000;
  }
  
  /**
   * 执行工具
   * @param {string} toolId - 工具ID
   * @param {Object} params - 工具参数
   * @param {Object} [options] - 执行选项
   * @returns {Promise<ToolResult>} 执行结果
   */
  async executeTool(toolId, params, options = {}) {
    const startTime = Date.now();
    let result;
    
    try {
      // 获取工具
      const tool = this.toolRegistry.getTool(toolId, options.providerId);
      if (!tool) {
        throw new Error(`未找到工具: ${toolId}`);
      }
      
      // 验证参数
      const validationResult = this.validator.validate(params, tool.paramSchema);
      if (!validationResult.valid) {
        throw new ValidationError('参数验证失败', validationResult.errors);
      }
      
      // 执行工具
      result = await tool.execute(params);
      
      // 添加执行时间
      if (!result.metadata) {
        result.metadata = {};
      }
      result.metadata.executionTime = Date.now() - startTime;
      
      // 记录执行历史
      this.recordExecution({
        toolId,
        params,
        result,
        startTime,
        endTime: Date.now(),
        success: result.success
      });
      
      return result;
    } catch (error) {
      // 构建错误结果
      result = {
        success: false,
        error: error.message,
        metadata: {
          executionTime: Date.now() - startTime,
          errorType: error.constructor.name,
          errorDetails: error instanceof ValidationError ? error.errors : undefined
        }
      };
      
      // 记录执行历史
      this.recordExecution({
        toolId,
        params,
        result,
        startTime,
        endTime: Date.now(),
        success: false,
        error: error
      });
      
      return result;
    }
  }
  
  /**
   * 记录执行历史
   * @param {Object} execution - 执行记录
   */
  recordExecution(execution) {
    this.executionHistory.push(execution);
    
    // 限制历史记录大小
    if (this.executionHistory.length > this.maxHistorySize) {
      this.executionHistory.shift();
    }
  }
  
  /**
   * 获取执行历史
   * @param {Object} [filters] - 过滤条件
   * @returns {Array} 过滤后的执行历史
   */
  getExecutionHistory(filters = {}) {
    let history = [...this.executionHistory];
    
    // 应用过滤器
    if (filters.toolId) {
      history = history.filter(record => record.toolId === filters.toolId);
    }
    
    if (filters.success !== undefined) {
      history = history.filter(record => record.success === filters.success);
    }
    
    if (filters.timeRange) {
      const { start, end } = filters.timeRange;
      history = history.filter(record => {
        return record.startTime >= start && record.startTime <= end;
      });
    }
    
    return history;
  }
  
  /**
   * 清除执行历史
   */
  clearExecutionHistory() {
    this.executionHistory = [];
  }
}

/**
 * 验证错误类
 */
class ValidationError extends Error {
  /**
   * 构造函数
   * @param {string} message - 错误消息
   * @param {ValidationError[]} errors - 验证错误列表
   */
  constructor(message, errors) {
    super(message);
    this.name = 'ValidationError';
    this.errors = errors;
  }
}
```