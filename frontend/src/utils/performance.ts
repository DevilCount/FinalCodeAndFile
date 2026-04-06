/**
 * 前端性能优化工具类
 * 包含图片懒加载、路由预加载等优化策略
 */

/**
 * 图片懒加载 IntersectionObserver 实现
 * @param selector CSS选择器，默认 img[data-src]
 */
export function lazyLoadImages(selector: string = 'img[data-src]') {
  if (!('IntersectionObserver' in window)) {
    // 降级处理：直接加载所有图片
    document.querySelectorAll<HTMLImageElement>(selector).forEach(img => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      }
    });
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          // 添加加载动画类
          img.classList.add('img-loaded');
        }
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: '50px 0px', // 提前50px加载
    threshold: 0.01
  });

  document.querySelectorAll<HTMLImageElement>(selector).forEach(img => {
    observer.observe(img);
  });

  return observer;
}

/**
 * 预加载指定路由组件
 * @param routes 需要预加载的路由名称数组
 */
export function preloadRoutes(routes: string[]) {
  // 这个函数需要配合路由配置使用
  // 在实际项目中，可以使用 router.getRoutes() 来获取路由并动态导入
  console.log('Preloading routes:', routes);
}

/**
 * 防抖函数
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return function (this: any, ...args: Parameters<T>) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
      timer = null;
    }, delay);
  };
}

/**
 * 节流函数
 * @param fn 要执行的函数
 * @param delay 间隔时间（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now();
    if (now - lastTime >= delay) {
      fn.apply(this, args);
      lastTime = now;
    }
  };
}

/**
 * 资源预加载
 * @param urls 资源URL数组
 */
export function preloadResources(urls: string[]) {
  urls.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    // 根据资源类型设置as属性
    if (url.endsWith('.css')) {
      link.as = 'style';
    } else if (url.endsWith('.js')) {
      link.as = 'script';
    } else if (/\.(jpg|jpeg|png|gif|webp|svg)$/.test(url)) {
      link.as = 'image';
    } else if (/\.(woff|woff2|ttf|otf)$/.test(url)) {
      link.as = 'font';
      link.crossOrigin = 'anonymous';
    }
    document.head.appendChild(link);
  });
}

/**
 * 请求缓存工具
 * 用于缓存GET请求结果
 */
class RequestCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private defaultTTL = 5 * 60 * 1000; // 默认5分钟

  /**
   * 设置缓存
   */
  set(key: string, data: any, ttl: number = this.defaultTTL) {
    this.cache.set(key, {
      data,
      timestamp: Date.now() + ttl
    });
  }

  /**
   * 获取缓存
   */
  get(key: string) {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() > cached.timestamp) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  /**
   * 清除缓存
   */
  clear(key?: string) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}

export const requestCache = new RequestCache();

/**
 * 初始化性能监控
 */
export function initPerformanceMonitoring() {
  if (window.performance) {
    // 页面加载完成后输出性能指标
    window.addEventListener('load', () => {
      setTimeout(() => {
        const timing = performance.timing;
        const performanceData = {
          // DNS查询耗时
          dns: timing.domainLookupEnd - timing.domainLookupStart,
          // TCP连接耗时
          tcp: timing.connectEnd - timing.connectStart,
          // 首包时间
          ttfb: timing.responseStart - timing.requestStart,
          // 下载时间
          download: timing.responseEnd - timing.responseStart,
          // DOM解析耗时
          domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
          // 页面完全加载时间
          load: timing.loadEventEnd - timing.navigationStart
        };
        
        console.log('Performance Metrics:', performanceData);
        
        // 可以将性能数据发送到后端进行分析
        // fetch('/api/performance', {
        //   method: 'POST',
        //   body: JSON.stringify(performanceData)
        // });
      }, 0);
    });
  }
}
