// 医疗系统专业组件库
export { default as LabResultDisplay } from './LabResultDisplay.vue'
export { default as PatientInfoCard } from './PatientInfoCard.vue'
export { default as SampleStatusBadge } from './SampleStatusBadge.vue'
export { default as ReportReviewPanel } from './ReportReviewPanel.vue'

// 组件安装函数（可选）
export function installMedicalComponents(app) {
  app.component('LabResultDisplay', LabResultDisplay)
  app.component('PatientInfoCard', PatientInfoCard)
  app.component('SampleStatusBadge', SampleStatusBadge)
  app.component('ReportReviewPanel', ReportReviewPanel)
}