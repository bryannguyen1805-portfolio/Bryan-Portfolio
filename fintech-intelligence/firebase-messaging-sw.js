/* Firebase Cloud Messaging Service Worker for Bnews Fintech Intelligence */
importScripts('https://www.gstatic.com/firebasejs/11.1.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/11.1.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'AIzaSyDlBDhAmI0dwxJBQAwXPh85pUX8wtkZcUI',
  authDomain: 'bnews-11b05.firebaseapp.com',
  projectId: 'bnews-11b05',
  storageBucket: 'bnews-11b05.firebasestorage.app',
  messagingSenderId: '484182584980',
  appId: '1:484182584980:web:2ab6dacdc8b920394c0e81'
});

const messaging = firebase.messaging();

const DEFAULT_BNEWS_URL = self.location.origin + (self.location.pathname.includes('/fintech-intelligence/') ? '/fintech-intelligence/' : '/');

messaging.onBackgroundMessage((payload) => {
  // Only show manually for data-only messages so FCM notification payloads never duplicate
  if (payload?.notification) return;
  const title = payload?.data?.title || 'Bnews · Ấn bản mới';
  const body = payload?.data?.body || 'Đã có 40 tin Tài chính – Ngân hàng & Thanh toán số hôm nay. Mở đọc bản tóm tắt 3 phút ngay →';
  const targetUrl = payload?.fcmOptions?.link || payload?.data?.url || DEFAULT_BNEWS_URL;

  self.registration.showNotification(title, {
    body,
    icon: 'fintech-favicon-192.png',
    badge: 'fintech-favicon-32.png',
    tag: payload?.data?.tag || 'bnews-daily-edition',
    data: { url: targetUrl }
  });
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = event.notification?.data?.url || DEFAULT_BNEWS_URL;
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (const client of windowClients) {
        if (client.url.startsWith(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(targetUrl);
    })
  );
});
