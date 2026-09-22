import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

const getBackendPort = () => {
  try {
    const configPath = path.resolve(__dirname, '../../../sites/common_site_config.json')
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'))
      if (config.webserver_port) {
        return config.webserver_port
      }
    }
  } catch (e) {
    console.error('Error reading common_site_config.json:', e)
  }
  return 8006 // Fallback
}

const backendPort = getBackendPort()

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3017,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true,
        headers: {
          'X-Frappe-Site-Name': 'wmspro.erpdata.in'
        }
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 3017,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true,
        headers: {
          'X-Frappe-Site-Name': 'wmspro.erpdata.in'
        }
      }
    }
  },
  define: {
    'import.meta.env.VITE_BACKEND_URL': JSON.stringify(`http://127.0.0.1:${backendPort}`)
  }
})
