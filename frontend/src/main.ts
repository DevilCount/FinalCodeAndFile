import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import './styles/element-plus-overrides.scss'
import './styles/pages-common.scss'

const app = createApp(App)
const pinia = createPinia()

// 使用持久化插件
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// 配置Element Plus主题
app.use(ElementPlus, {
  zIndex: 3000,
  button: {
    autoInsertSpace: true
  }
})

app.mount('#app')
