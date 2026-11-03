/* Plan 5.5: Web Push reminders - imported into the generated service worker (vite.config.ts). */
self.addEventListener('push', (event) => {
  let data = {}
  try { data = event.data ? event.data.json() : {} } catch { data = { body: event.data && event.data.text() } }
  event.waitUntil(self.registration.showNotification(data.title || 'LookCoach', {
    body: data.body || '',
    data: { url: data.url || '/' },
    tag: data.title || 'lookcoach',
  }))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = (event.notification.data && event.notification.data.url) || '/'
  event.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
    for (const client of list) {
      if ('focus' in client) { client.navigate(url); return client.focus() }
    }
    return self.clients.openWindow(url)
  }))
})
