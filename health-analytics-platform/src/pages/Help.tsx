import { useState } from 'react'
import { HelpCircle, Book, Keyboard, Bell, ChevronDown, ChevronRight } from 'lucide-react'

interface FAQItem {
  question: string
  answer: string
}

const faqs: FAQItem[] = [
  {
    question: 'What is InfraSense?',
    answer: 'InfraSense is a real-time health analytics platform that monitors your infrastructure components, provides predictive warnings, and helps you identify issues before they become critical.',
  },
  {
    question: 'How does the predictive warning system work?',
    answer: 'Our AI analyzes historical data patterns to predict when a component might exceed its threshold. The prediction includes confidence level and time to breach, helping you take proactive measures.',
  },
  {
    question: 'What do the health scores mean?',
    answer: 'Health scores range from 0-100%. 90%+ is healthy, 70-89% is degraded/warning, and below 70% is critical. Scores are calculated based on CPU, memory, and disk usage.',
  },
  {
    question: 'How do I acknowledge or resolve an alert?',
    answer: 'Click on any alert to open its details. Use the "Acknowledge" button to mark that you are working on it, and "Resolve" when the issue is fixed.',
  },
  {
    question: 'Can I export data from the dashboard?',
    answer: 'Yes! Use the export button in the dashboard header to download data as JSON or CSV. You can also export reports from the Reports page.',
  },
  {
    question: 'How often is the data refreshed?',
    answer: 'By default, data refreshes every 30 seconds. You can adjust this in Settings. The "Live" indicator shows the current update status.',
  },
]

const shortcuts = [
  { key: 'Ctrl + R', action: 'Refresh dashboard data' },
  { key: 'Escape', action: 'Close open modal or detail view' },
  { key: 'Ctrl + F', action: 'Focus search input' },
]

export function Help() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-4xl">
        <h1 className="text-2xl font-semibold text-[#111111] mb-1">Help & Documentation</h1>
        <p className="text-sm text-[#8A8A8A] mb-6">Learn how to use InfraSense effectively</p>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="border border-[#E5E5E5] rounded-xl p-4 hover:border-[#FF7900] transition-colors cursor-pointer">
            <Book className="w-6 h-6 text-[#FF7900] mb-2" />
            <h3 className="font-semibold text-[#111111]">Getting Started</h3>
            <p className="text-sm text-[#8A8A8A]">Learn the basics</p>
          </div>
          <div className="border border-[#E5E5E5] rounded-xl p-4 hover:border-[#FF7900] transition-colors cursor-pointer">
            <Keyboard className="w-6 h-6 text-[#FF7900] mb-2" />
            <h3 className="font-semibold text-[#111111]">Keyboard Shortcuts</h3>
            <p className="text-sm text-[#8A8A8A]">Work faster</p>
          </div>
          <div className="border border-[#E5E5E5] rounded-xl p-4 hover:border-[#FF7900] transition-colors cursor-pointer">
            <Bell className="w-6 h-6 text-[#FF7900] mb-2" />
            <h3 className="font-semibold text-[#111111]">Alert Management</h3>
            <p className="text-sm text-[#8A8A8A]">Handle alerts</p>
          </div>
        </div>

        <div className="border border-[#E5E5E5] rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold text-[#111111] mb-4">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div key={idx} className="border border-[#E5E5E5] rounded-lg overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-[#F7F7F7] transition-colors"
                >
                  <span className="font-medium text-[#111111]">{faq.question}</span>
                  {openFaq === idx ? (
                    <ChevronDown className="w-5 h-5 text-[#8A8A8A]" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-[#8A8A8A]" />
                  )}
                </button>
                {openFaq === idx && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-[#8A8A8A]">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="border border-[#E5E5E5] rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold text-[#111111] mb-4">Keyboard Shortcuts</h2>
          <div className="space-y-3">
            {shortcuts.map(({ key, action }) => (
              <div key={key} className="flex items-center justify-between p-3 bg-[#F7F7F7] rounded-lg">
                <span className="text-sm text-[#111111]">{action}</span>
                <kbd className="px-2 py-1 bg-white border border-[#E5E5E5] rounded text-xs font-mono">{key}</kbd>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-[#E5E5E5] rounded-xl p-6">
          <h2 className="text-lg font-semibold text-[#111111] mb-4">Need More Help?</h2>
          <p className="text-sm text-[#8A8A8A] mb-4">
            If you can't find what you're looking for, please contact our support team.
          </p>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#FF7900] text-white rounded-lg hover:bg-[#FF7900]/90 transition-colors">
            <HelpCircle className="w-4 h-4" />
            Contact Support
          </button>
        </div>
      </div>
    </div>
  )
}