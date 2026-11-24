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

messaging.onBackgroundMessage((payload) => {
  const title = payload?.notification?.title || payload?.data?.title || 'Bnews · FinTech Intelligence';
  const body = payload?.notification?.body || payload?.data?.body || 'Ấn bản tài chính mới đã được xuất bản.';
  const targetUrl = payload?.fcmOptions?.link || payload?.data?.url || 'https://bryanportfolio.io.vn/fintech-intelligence/';

  self.registration.showNotification(title, {
    body,
    icon: '/fintech-intelligence/fintech-favicon-192.png',
    badge: '/fintech-intelligence/fintech-favicon-32.png',
    data: { url: targetUrl }
  });
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = event.notification?.data?.url || 'https://bryanportfolio.io.vn/fintech-intelligence/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (const client of windowClients) {
        if (client.url.includes('/fintech-intelligence') && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(targetUrl);
    })
  );
});
