import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8086',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/user': {
          target: 'http://localhost:8086',
          changeOrigin: true
        }
      },
      // 预热常用模块，加快开发启动速度
      warmup: {
        clientFiles: [
          './src/main.ts',
          './src/App.vue',
          './src/router/index.ts',
          './src/api/index.ts'
        ]
      }
    },
    
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: 'esbuild',  // 使用esbuild替代terser（无需额外安装依赖）
      // 启用gzip压缩提示大小
      reportCompressedSize: true,
      // 块大小警告阈值
      chunkSizeWarningLimit: 1000,
      // 目标浏览器
      target: 'es2015',
      // CSS代码分割
      cssCodeSplit: true,

      rollupOptions: {
        output: {
          // 更精细的代码分割策略
          manualChunks: {
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus'],
            'element-plus-icons': ['@element-plus/icons-vue'],
            'echarts': ['echarts'],
            'utils': ['axios', 'vee-validate']
          },
          // 分割小块，提高缓存命中率
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        },
        // 外部化不需要打包的依赖
        external: []
      }
    },
    
    // 优化依赖预构建
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'element-plus',
        'echarts',
        'axios',
        'vee-validate'
      ],
      exclude: []
    },
    
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`
        }
      },
      // 开发环境启用CSS源映射
      devSourcemap: true
    }
  }
})
