/**
 * Bryan News | Fintech Intelligence — V4.0 Clean Institutional UI Pilot
 * Isolated preview reading live ../edition-data.json with ../edition-data.js fallback.
 */
'use strict';

(() => {
  const CATEGORIES = [
    { key: 'Thanh toán', label: 'Thanh toán số' },
    { key: 'Ngân hàng', label: 'Ngân hàng' },
    { key: 'Thị trường vốn', label: 'Thị trường vốn' },
    { key: 'Doanh nghiệp', label: 'Doanh nghiệp' },
    { key: 'Kinh tế vĩ mô', label: 'Kinh tế vĩ mô' },
    { key: 'Bán lẻ, D2C và xu hướng tiêu dùng', label: 'Bán lẻ & Tiêu dùng' }
  ];

  const CAT_LABEL_MAP = Object.fromEntries(CATEGORIES.map(c => [c.key, c.label]));

  const BNEWS_SUBSCRIBE_WEBHOOK_URL =
    'https://script.google.com/macros/s/AKfycbwzarTCq14B7wgY3LjdBjLpWFP8hNH1xSGdwybkxCDigKdz12P60YRnBVFy9yi4uFL4/exec';
  const WELCOME_STORAGE_KEY = 'bryan_fintech_welcome_shown_v4';

  const QR_SVG_DATA = {
    vcard: {
      size: 71,
      color: '#292524',
      path: 'M1,1h7v1h-7zM9,1h2v1h-2zM12,1h1v1h-1zM14,1h1v1h-1zM17,1h1v1h-1zM21,1h1v1h-1zM23,1h2v1h-2zM26,1h1v1h-1zM30,1h1v1h-1zM35,1h1v1h-1zM37,1h2v1h-2zM41,1h2v1h-2zM45,1h3v1h-3zM50,1h2v1h-2zM54,1h2v1h-2zM60,1h2v1h-2zM64,1h1v1h-1zM67,1h3v1h-3zM1,2h1v1h-1zM7,2h1v1h-1zM12,2h1v1h-1zM15,2h3v1h-3zM19,2h1v1h-1zM22,2h2v1h-2zM29,2h3v1h-3zM35,2h1v1h-1zM37,2h2v1h-2zM40,2h1v1h-1zM42,2h1v1h-1zM44,2h3v1h-3zM50,2h1v1h-1zM52,2h2v1h-2zM58,2h7v1h-7zM66,2h1v1h-1zM69,2h1v1h-1zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM10,3h4v1h-4zM18,3h1v1h-1zM21,3h2v1h-2zM24,3h1v1h-1zM26,3h2v1h-2zM31,3h1v1h-1zM33,3h5v1h-5zM39,3h2v1h-2zM42,3h3v1h-3zM46,3h1v1h-1zM48,3h1v1h-1zM50,3h2v1h-2zM53,3h1v1h-1zM57,3h1v1h-1zM59,3h2v1h-2zM63,3h1v1h-1zM65,3h3v1h-3zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM11,4h1v1h-1zM15,4h2v1h-2zM19,4h2v1h-2zM23,4h1v1h-1zM30,4h2v1h-2zM34,4h1v1h-1zM40,4h2v1h-2zM43,4h4v1h-4zM49,4h1v1h-1zM51,4h1v1h-1zM58,4h1v1h-1zM60,4h3v1h-3zM64,4h1v1h-1zM67,4h3v1h-3zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h3v1h-3zM13,5h3v1h-3zM20,5h1v1h-1zM24,5h3v1h-3zM29,5h2v1h-2zM33,5h6v1h-6zM47,5h1v1h-1zM50,5h1v1h-1zM57,5h1v1h-1zM59,5h1v1h-1zM61,5h5v1h-5zM67,5h1v1h-1zM69,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM11,6h1v1h-1zM14,6h2v1h-2zM19,6h1v1h-1zM21,6h5v1h-5zM29,6h3v1h-3zM33,6h1v1h-1zM37,6h2v1h-2zM40,6h1v1h-1zM42,6h1v1h-1zM44,6h1v1h-1zM46,6h4v1h-4zM51,6h2v1h-2zM54,6h1v1h-1zM57,6h1v1h-1zM59,6h1v1h-1zM61,6h1v1h-1zM65,6h3v1h-3zM69,6h1v1h-1zM1,7h7v1h-7zM9,7h2v1h-2zM12,7h3v1h-3zM17,7h1v1h-1zM22,7h1v1h-1zM24,7h4v1h-4zM29,7h2v1h-2zM32,7h2v1h-2zM35,7h1v1h-1zM37,7h4v1h-4zM42,7h1v1h-1zM46,7h1v1h-1zM50,7h2v1h-2zM54,7h2v1h-2zM57,7h1v1h-1zM61,7h1v1h-1zM63,7h1v1h-1zM65,7h3v1h-3zM9,8h3v1h-3zM14,8h1v1h-1zM19,8h6v1h-6zM26,8h2v1h-2zM32,8h2v1h-2zM37,8h1v1h-1zM39,8h2v1h-2zM43,8h1v1h-1zM46,8h1v1h-1zM50,8h2v1h-2zM53,8h3v1h-3zM58,8h2v1h-2zM61,8h1v1h-1zM65,8h1v1h-1zM67,8h1v1h-1zM69,8h1v1h-1zM1,9h1v1h-1zM4,9h2v1h-2zM7,9h2v1h-2zM11,9h1v1h-1zM14,9h1v1h-1zM16,9h1v1h-1zM18,9h1v1h-1zM23,9h1v1h-1zM25,9h1v1h-1zM28,9h1v1h-1zM31,9h8v1h-8zM41,9h1v1h-1zM44,9h2v1h-2zM47,9h2v1h-2zM52,9h1v1h-1zM54,9h2v1h-2zM57,9h1v1h-1zM60,9h7v1h-7zM69,9h1v1h-1zM1,10h1v1h-1zM8,10h2v1h-2zM11,10h3v1h-3zM15,10h1v1h-1zM19,10h3v1h-3zM24,10h2v1h-2zM27,10h1v1h-1zM29,10h1v1h-1zM31,10h2v1h-2zM35,10h1v1h-1zM38,10h1v1h-1zM42,10h1v1h-1zM44,10h4v1h-4zM49,10h1v1h-1zM52,10h2v1h-2zM56,10h2v1h-2zM59,10h2v1h-2zM63,10h1v1h-1zM65,10h1v1h-1zM69,10h1v1h-1zM1,11h1v1h-1zM3,11h1v1h-1zM5,11h8v1h-8zM15,11h4v1h-4zM20,11h1v1h-1zM23,11h1v1h-1zM25,11h2v1h-2zM28,11h6v1h-6zM35,11h5v1h-5zM44,11h1v1h-1zM46,11h1v1h-1zM50,11h5v1h-5zM57,11h5v1h-5zM63,11h1v1h-1zM65,11h1v1h-1zM2,12h2v1h-2zM5,12h1v1h-1zM9,12h1v1h-1zM12,12h2v1h-2zM15,12h1v1h-1zM19,12h3v1h-3zM24,12h1v1h-1zM26,12h3v1h-3zM30,12h1v1h-1zM32,12h3v1h-3zM37,12h1v1h-1zM39,12h1v1h-1zM41,12h5v1h-5zM47,12h1v1h-1zM49,12h1v1h-1zM51,12h2v1h-2zM54,12h2v1h-2zM60,12h1v1h-1zM62,12h3v1h-3zM66,12h2v1h-2zM69,12h1v1h-1zM1,13h1v1h-1zM3,13h3v1h-3zM7,13h1v1h-1zM9,13h1v1h-1zM15,13h5v1h-5zM21,13h1v1h-1zM24,13h2v1h-2zM27,13h2v1h-2zM30,13h3v1h-3zM34,13h1v1h-1zM36,13h3v1h-3zM40,13h11v1h-11zM52,13h1v1h-1zM54,13h4v1h-4zM59,13h1v1h-1zM62,13h2v1h-2zM67,13h1v1h-1zM69,13h1v1h-1zM1,14h1v1h-1zM5,14h1v1h-1zM8,14h1v1h-1zM10,14h1v1h-1zM12,14h2v1h-2zM16,14h2v1h-2zM19,14h3v1h-3zM23,14h1v1h-1zM26,14h4v1h-4zM31,14h2v1h-2zM34,14h1v1h-1zM38,14h1v1h-1zM40,14h2v1h-2zM45,14h5v1h-5zM54,14h1v1h-1zM56,14h1v1h-1zM58,14h2v1h-2zM62,14h3v1h-3zM66,14h1v1h-1zM1,15h1v1h-1zM4,15h1v1h-1zM7,15h1v1h-1zM9,15h1v1h-1zM12,15h2v1h-2zM15,15h2v1h-2zM20,15h1v1h-1zM23,15h1v1h-1zM27,15h5v1h-5zM33,15h1v1h-1zM35,15h1v1h-1zM37,15h2v1h-2zM41,15h1v1h-1zM44,15h1v1h-1zM46,15h3v1h-3zM51,15h4v1h-4zM58,15h3v1h-3zM62,15h1v1h-1zM65,15h1v1h-1zM68,15h1v1h-1zM3,16h4v1h-4zM9,16h2v1h-2zM12,16h1v1h-1zM14,16h2v1h-2zM18,16h1v1h-1zM23,16h1v1h-1zM25,16h2v1h-2zM29,16h2v1h-2zM32,16h1v1h-1zM34,16h1v1h-1zM37,16h3v1h-3zM43,16h2v1h-2zM46,16h1v1h-1zM48,16h2v1h-2zM51,16h2v1h-2zM55,16h2v1h-2zM58,16h1v1h-1zM63,16h1v1h-1zM65,16h1v1h-1zM67,16h1v1h-1zM69,16h1v1h-1zM1,17h4v1h-4zM7,17h4v1h-4zM12,17h2v1h-2zM16,17h3v1h-3zM23,17h3v1h-3zM27,17h1v1h-1zM29,17h1v1h-1zM31,17h4v1h-4zM36,17h2v1h-2zM39,17h3v1h-3zM44,17h1v1h-1zM46,17h1v1h-1zM52,17h1v1h-1zM54,17h1v1h-1zM56,17h1v1h-1zM58,17h1v1h-1zM61,17h2v1h-2zM66,17h2v1h-2zM69,17h1v1h-1zM1,18h1v1h-1zM9,18h1v1h-1zM16,18h2v1h-2zM20,18h1v1h-1zM22,18h2v1h-2zM25,18h2v1h-2zM28,18h1v1h-1zM31,18h1v1h-1zM34,18h1v1h-1zM37,18h1v1h-1zM40,18h1v1h-1zM44,18h1v1h-1zM47,18h2v1h-2zM51,18h1v1h-1zM54,18h2v1h-2zM60,18h2v1h-2zM64,18h3v1h-3zM1,19h1v1h-1zM4,19h1v1h-1zM6,19h4v1h-4zM12,19h2v1h-2zM15,19h2v1h-2zM22,19h2v1h-2zM25,19h2v1h-2zM30,19h1v1h-1zM33,19h1v1h-1zM35,19h1v1h-1zM38,19h1v1h-1zM41,19h4v1h-4zM46,19h1v1h-1zM48,19h2v1h-2zM52,19h1v1h-1zM55,19h1v1h-1zM60,19h3v1h-3zM67,19h2v1h-2zM2,20h1v1h-1zM5,20h1v1h-1zM8,20h1v1h-1zM10,20h1v1h-1zM12,20h1v1h-1zM14,20h1v1h-1zM16,20h1v1h-1zM18,20h1v1h-1zM21,20h7v1h-7zM29,20h1v1h-1zM31,20h3v1h-3zM37,20h3v1h-3zM41,20h1v1h-1zM44,20h1v1h-1zM46,20h1v1h-1zM49,20h1v1h-1zM51,20h8v1h-8zM61,20h1v1h-1zM64,20h1v1h-1zM67,20h1v1h-1zM69,20h1v1h-1zM1,21h3v1h-3zM7,21h1v1h-1zM14,21h1v1h-1zM19,21h2v1h-2zM22,21h1v1h-1zM25,21h2v1h-2zM29,21h9v1h-9zM40,21h2v1h-2zM43,21h1v1h-1zM45,21h2v1h-2zM48,21h2v1h-2zM51,21h2v1h-2zM54,21h1v1h-1zM56,21h3v1h-3zM60,21h1v1h-1zM62,21h5v1h-5zM68,21h2v1h-2zM1,22h1v1h-1zM3,22h1v1h-1zM6,22h1v1h-1zM9,22h1v1h-1zM13,22h1v1h-1zM15,22h1v1h-1zM18,22h2v1h-2zM23,22h1v1h-1zM25,22h1v1h-1zM27,22h3v1h-3zM31,22h1v1h-1zM34,22h1v1h-1zM36,22h2v1h-2zM39,22h2v1h-2zM42,22h1v1h-1zM44,22h1v1h-1zM47,22h1v1h-1zM50,22h2v1h-2zM54,22h1v1h-1zM64,22h1v1h-1zM66,22h1v1h-1zM68,22h2v1h-2zM3,23h2v1h-2zM7,23h1v1h-1zM10,23h2v1h-2zM14,23h1v1h-1zM17,23h1v1h-1zM19,23h1v1h-1zM22,23h1v1h-1zM25,23h1v1h-1zM33,23h1v1h-1zM36,23h1v1h-1zM38,23h2v1h-2zM41,23h1v1h-1zM46,23h1v1h-1zM48,23h2v1h-2zM53,23h4v1h-4zM63,23h1v1h-1zM67,23h2v1h-2zM2,24h1v1h-1zM4,24h3v1h-3zM8,24h3v1h-3zM12,24h1v1h-1zM14,24h1v1h-1zM16,24h1v1h-1zM18,24h1v1h-1zM21,24h4v1h-4zM27,24h1v1h-1zM29,24h1v1h-1zM31,24h4v1h-4zM36,24h1v1h-1zM39,24h1v1h-1zM41,24h1v1h-1zM43,24h3v1h-3zM47,24h1v1h-1zM50,24h2v1h-2zM54,24h2v1h-2zM57,24h2v1h-2zM60,24h2v1h-2zM63,24h2v1h-2zM67,24h3v1h-3zM1,25h1v1h-1zM4,25h2v1h-2zM7,25h8v1h-8zM20,25h1v1h-1zM24,25h1v1h-1zM26,25h2v1h-2zM30,25h1v1h-1zM32,25h1v1h-1zM40,25h8v1h-8zM50,25h1v1h-1zM54,25h1v1h-1zM57,25h2v1h-2zM62,25h7v1h-7zM1,26h2v1h-2zM4,26h1v1h-1zM8,26h3v1h-3zM12,26h1v1h-1zM14,26h1v1h-1zM16,26h1v1h-1zM20,26h2v1h-2zM24,26h1v1h-1zM28,26h1v1h-1zM30,26h1v1h-1zM32,26h2v1h-2zM37,26h1v1h-1zM39,26h2v1h-2zM42,26h1v1h-1zM46,26h4v1h-4zM52,26h4v1h-4zM58,26h2v1h-2zM61,26h1v1h-1zM64,26h3v1h-3zM68,26h2v1h-2zM1,27h1v1h-1zM4,27h2v1h-2zM7,27h4v1h-4zM12,27h2v1h-2zM16,27h1v1h-1zM24,27h1v1h-1zM27,27h1v1h-1zM32,27h1v1h-1zM34,27h1v1h-1zM36,27h1v1h-1zM38,27h1v1h-1zM41,27h2v1h-2zM46,27h1v1h-1zM48,27h4v1h-4zM53,27h1v1h-1zM55,27h2v1h-2zM58,27h2v1h-2zM61,27h1v1h-1zM64,27h2v1h-2zM67,27h1v1h-1zM69,27h1v1h-1zM2,28h2v1h-2zM5,28h2v1h-2zM11,28h1v1h-1zM13,28h2v1h-2zM18,28h3v1h-3zM23,28h1v1h-1zM25,28h2v1h-2zM31,28h1v1h-1zM35,28h3v1h-3zM40,28h1v1h-1zM42,28h1v1h-1zM45,28h1v1h-1zM47,28h2v1h-2zM54,28h2v1h-2zM57,28h2v1h-2zM60,28h2v1h-2zM63,28h1v1h-1zM65,28h1v1h-1zM67,28h1v1h-1zM69,28h1v1h-1zM3,29h2v1h-2zM7,29h2v1h-2zM12,29h1v1h-1zM14,29h4v1h-4zM20,29h2v1h-2zM24,29h3v1h-3zM29,29h1v1h-1zM32,29h3v1h-3zM36,29h1v1h-1zM39,29h1v1h-1zM42,29h2v1h-2zM46,29h2v1h-2zM50,29h1v1h-1zM52,29h1v1h-1zM54,29h1v1h-1zM56,29h4v1h-4zM63,29h1v1h-1zM66,29h1v1h-1zM68,29h1v1h-1zM1,30h1v1h-1zM4,30h2v1h-2zM9,30h1v1h-1zM12,30h3v1h-3zM16,30h1v1h-1zM19,30h1v1h-1zM21,30h3v1h-3zM27,30h7v1h-7zM39,30h1v1h-1zM42,30h3v1h-3zM46,30h5v1h-5zM53,30h2v1h-2zM57,30h5v1h-5zM64,30h6v1h-6zM4,31h2v1h-2zM7,31h2v1h-2zM10,31h2v1h-2zM13,31h2v1h-2zM18,31h2v1h-2zM21,31h2v1h-2zM24,31h2v1h-2zM30,31h1v1h-1zM32,31h1v1h-1zM34,31h2v1h-2zM40,31h1v1h-1zM50,31h6v1h-6zM60,31h1v1h-1zM65,31h1v1h-1zM67,31h2v1h-2zM1,32h1v1h-1zM4,32h1v1h-1zM6,32h1v1h-1zM8,32h2v1h-2zM11,32h1v1h-1zM13,32h1v1h-1zM15,32h2v1h-2zM19,32h1v1h-1zM24,32h1v1h-1zM26,32h2v1h-2zM34,32h1v1h-1zM36,32h2v1h-2zM39,32h1v1h-1zM41,32h3v1h-3zM46,32h1v1h-1zM48,32h3v1h-3zM52,32h2v1h-2zM55,32h2v1h-2zM60,32h1v1h-1zM64,32h1v1h-1zM67,32h1v1h-1zM2,33h1v1h-1zM4,33h11v1h-11zM16,33h1v1h-1zM18,33h1v1h-1zM20,33h4v1h-4zM27,33h1v1h-1zM31,33h8v1h-8zM40,33h1v1h-1zM42,33h1v1h-1zM45,33h3v1h-3zM53,33h2v1h-2zM56,33h10v1h-10zM67,33h3v1h-3zM3,34h1v1h-1zM5,34h1v1h-1zM9,34h1v1h-1zM12,34h1v1h-1zM15,34h2v1h-2zM20,34h3v1h-3zM26,34h5v1h-5zM33,34h1v1h-1zM37,34h1v1h-1zM39,34h2v1h-2zM42,34h1v1h-1zM47,34h3v1h-3zM54,34h1v1h-1zM58,34h2v1h-2zM61,34h1v1h-1zM65,34h1v1h-1zM68,34h2v1h-2zM3,35h3v1h-3zM7,35h1v1h-1zM9,35h2v1h-2zM12,35h1v1h-1zM15,35h1v1h-1zM17,35h1v1h-1zM19,35h1v1h-1zM21,35h1v1h-1zM24,35h1v1h-1zM27,35h1v1h-1zM29,35h1v1h-1zM32,35h2v1h-2zM35,35h1v1h-1zM37,35h2v1h-2zM40,35h4v1h-4zM46,35h1v1h-1zM50,35h2v1h-2zM53,35h3v1h-3zM57,35h5v1h-5zM63,35h1v1h-1zM65,35h1v1h-1zM67,35h2v1h-2zM1,36h3v1h-3zM5,36h1v1h-1zM9,36h3v1h-3zM14,36h2v1h-2zM17,36h1v1h-1zM21,36h1v1h-1zM26,36h1v1h-1zM30,36h4v1h-4zM37,36h1v1h-1zM39,36h3v1h-3zM45,36h1v1h-1zM49,36h3v1h-3zM53,36h1v1h-1zM56,36h2v1h-2zM60,36h2v1h-2zM65,36h3v1h-3zM1,37h1v1h-1zM5,37h5v1h-5zM11,37h2v1h-2zM20,37h1v1h-1zM24,37h2v1h-2zM27,37h2v1h-2zM31,37h8v1h-8zM41,37h2v1h-2zM45,37h4v1h-4zM51,37h1v1h-1zM54,37h1v1h-1zM56,37h1v1h-1zM59,37h8v1h-8zM68,37h2v1h-2zM2,38h5v1h-5zM12,38h2v1h-2zM16,38h1v1h-1zM18,38h1v1h-1zM20,38h1v1h-1zM26,38h2v1h-2zM29,38h1v1h-1zM33,38h3v1h-3zM37,38h2v1h-2zM40,38h3v1h-3zM45,38h2v1h-2zM49,38h2v1h-2zM53,38h2v1h-2zM57,38h3v1h-3zM61,38h2v1h-2zM64,38h2v1h-2zM68,38h1v1h-1zM4,39h6v1h-6zM11,39h1v1h-1zM13,39h2v1h-2zM16,39h1v1h-1zM20,39h1v1h-1zM22,39h4v1h-4zM30,39h1v1h-1zM32,39h1v1h-1zM38,39h3v1h-3zM47,39h1v1h-1zM51,39h3v1h-3zM57,39h1v1h-1zM60,39h2v1h-2zM63,39h1v1h-1zM65,39h4v1h-4zM1,40h1v1h-1zM4,40h3v1h-3zM8,40h4v1h-4zM17,40h4v1h-4zM22,40h1v1h-1zM25,40h3v1h-3zM29,40h1v1h-1zM31,40h1v1h-1zM33,40h1v1h-1zM35,40h3v1h-3zM40,40h8v1h-8zM49,40h1v1h-1zM51,40h1v1h-1zM53,40h1v1h-1zM60,40h5v1h-5zM66,40h3v1h-3zM1,41h3v1h-3zM7,41h1v1h-1zM9,41h3v1h-3zM13,41h1v1h-1zM15,41h3v1h-3zM22,41h1v1h-1zM26,41h1v1h-1zM28,41h1v1h-1zM31,41h2v1h-2zM37,41h2v1h-2zM43,41h4v1h-4zM48,41h4v1h-4zM56,41h5v1h-5zM67,41h1v1h-1zM69,41h1v1h-1zM1,42h2v1h-2zM6,42h1v1h-1zM8,42h1v1h-1zM11,42h1v1h-1zM14,42h4v1h-4zM19,42h1v1h-1zM22,42h5v1h-5zM29,42h1v1h-1zM33,42h2v1h-2zM36,42h3v1h-3zM40,42h1v1h-1zM42,42h1v1h-1zM46,42h1v1h-1zM48,42h3v1h-3zM52,42h2v1h-2zM59,42h1v1h-1zM62,42h1v1h-1zM65,42h2v1h-2zM69,42h1v1h-1zM1,43h1v1h-1zM3,43h2v1h-2zM6,43h2v1h-2zM9,43h2v1h-2zM12,43h2v1h-2zM16,43h1v1h-1zM20,43h1v1h-1zM22,43h1v1h-1zM24,43h1v1h-1zM26,43h1v1h-1zM30,43h1v1h-1zM32,43h1v1h-1zM36,43h2v1h-2zM39,43h4v1h-4zM47,43h2v1h-2zM50,43h6v1h-6zM57,43h2v1h-2zM60,43h3v1h-3zM65,43h5v1h-5zM1,44h6v1h-6zM8,44h1v1h-1zM12,44h1v1h-1zM14,44h2v1h-2zM17,44h2v1h-2zM20,44h2v1h-2zM23,44h3v1h-3zM27,44h2v1h-2zM30,44h3v1h-3zM36,44h2v1h-2zM40,44h2v1h-2zM44,44h1v1h-1zM47,44h1v1h-1zM51,44h2v1h-2zM57,44h1v1h-1zM59,44h2v1h-2zM63,44h2v1h-2zM67,44h2v1h-2zM1,45h4v1h-4zM6,45h2v1h-2zM11,45h1v1h-1zM13,45h2v1h-2zM17,45h1v1h-1zM19,45h5v1h-5zM28,45h1v1h-1zM30,45h2v1h-2zM34,45h1v1h-1zM36,45h4v1h-4zM47,45h1v1h-1zM49,45h1v1h-1zM55,45h1v1h-1zM57,45h1v1h-1zM64,45h1v1h-1zM66,45h1v1h-1zM69,45h1v1h-1zM5,46h2v1h-2zM10,46h1v1h-1zM12,46h2v1h-2zM16,46h1v1h-1zM20,46h1v1h-1zM22,46h1v1h-1zM24,46h1v1h-1zM26,46h1v1h-1zM28,46h2v1h-2zM31,46h1v1h-1zM34,46h5v1h-5zM40,46h2v1h-2zM45,46h2v1h-2zM48,46h1v1h-1zM51,46h4v1h-4zM56,46h5v1h-5zM62,46h1v1h-1zM64,46h2v1h-2zM67,46h1v1h-1zM69,46h1v1h-1zM1,47h1v1h-1zM3,47h1v1h-1zM5,47h1v1h-1zM7,47h3v1h-3zM11,47h2v1h-2zM14,47h1v1h-1zM16,47h1v1h-1zM18,47h1v1h-1zM20,47h2v1h-2zM24,47h1v1h-1zM27,47h1v1h-1zM30,47h1v1h-1zM34,47h1v1h-1zM36,47h2v1h-2zM39,47h4v1h-4zM44,47h1v1h-1zM47,47h1v1h-1zM50,47h6v1h-6zM60,47h4v1h-4zM65,47h1v1h-1zM67,47h3v1h-3zM1,48h1v1h-1zM3,48h2v1h-2zM6,48h1v1h-1zM8,48h1v1h-1zM10,48h3v1h-3zM15,48h2v1h-2zM19,48h2v1h-2zM22,48h1v1h-1zM26,48h2v1h-2zM29,48h1v1h-1zM31,48h4v1h-4zM36,48h2v1h-2zM40,48h1v1h-1zM42,48h2v1h-2zM51,48h3v1h-3zM55,48h1v1h-1zM58,48h1v1h-1zM63,48h6v1h-6zM1,49h3v1h-3zM6,49h2v1h-2zM11,49h3v1h-3zM16,49h1v1h-1zM23,49h1v1h-1zM29,49h1v1h-1zM31,49h1v1h-1zM35,49h1v1h-1zM37,49h3v1h-3zM42,49h1v1h-1zM44,49h2v1h-2zM50,49h1v1h-1zM55,49h2v1h-2zM59,49h3v1h-3zM66,49h2v1h-2zM69,49h1v1h-1zM2,50h5v1h-5zM9,50h1v1h-1zM12,50h2v1h-2zM16,50h1v1h-1zM19,50h1v1h-1zM25,50h2v1h-2zM29,50h1v1h-1zM31,50h4v1h-4zM38,50h1v1h-1zM41,50h1v1h-1zM45,50h2v1h-2zM53,50h2v1h-2zM56,50h1v1h-1zM59,50h1v1h-1zM64,50h1v1h-1zM67,50h1v1h-1zM69,50h1v1h-1zM1,51h1v1h-1zM5,51h1v1h-1zM7,51h2v1h-2zM11,51h1v1h-1zM13,51h1v1h-1zM15,51h2v1h-2zM18,51h1v1h-1zM21,51h1v1h-1zM24,51h2v1h-2zM27,51h1v1h-1zM29,51h3v1h-3zM34,51h2v1h-2zM37,51h1v1h-1zM40,51h2v1h-2zM44,51h1v1h-1zM46,51h1v1h-1zM48,51h1v1h-1zM50,51h3v1h-3zM54,51h1v1h-1zM58,51h5v1h-5zM65,51h1v1h-1zM68,51h2v1h-2zM1,52h2v1h-2zM4,52h1v1h-1zM9,52h6v1h-6zM16,52h1v1h-1zM19,52h2v1h-2zM23,52h3v1h-3zM27,52h2v1h-2zM30,52h1v1h-1zM32,52h1v1h-1zM36,52h2v1h-2zM40,52h2v1h-2zM44,52h1v1h-1zM46,52h2v1h-2zM51,52h1v1h-1zM54,52h1v1h-1zM56,52h3v1h-3zM63,52h2v1h-2zM68,52h1v1h-1zM2,53h2v1h-2zM7,53h1v1h-1zM10,53h2v1h-2zM13,53h2v1h-2zM16,53h1v1h-1zM20,53h3v1h-3zM24,53h1v1h-1zM30,53h2v1h-2zM34,53h1v1h-1zM38,53h1v1h-1zM41,53h2v1h-2zM45,53h1v1h-1zM47,53h1v1h-1zM52,53h1v1h-1zM54,53h1v1h-1zM56,53h8v1h-8zM65,53h2v1h-2zM69,53h1v1h-1zM3,54h3v1h-3zM11,54h4v1h-4zM16,54h3v1h-3zM20,54h3v1h-3zM24,54h1v1h-1zM27,54h3v1h-3zM31,54h2v1h-2zM34,54h1v1h-1zM38,54h3v1h-3zM44,54h1v1h-1zM47,54h1v1h-1zM49,54h1v1h-1zM51,54h1v1h-1zM53,54h2v1h-2zM59,54h2v1h-2zM65,54h1v1h-1zM1,55h1v1h-1zM3,55h1v1h-1zM6,55h4v1h-4zM12,55h1v1h-1zM14,55h1v1h-1zM16,55h2v1h-2zM19,55h6v1h-6zM26,55h1v1h-1zM30,55h4v1h-4zM38,55h5v1h-5zM44,55h1v1h-1zM46,55h3v1h-3zM50,55h4v1h-4zM55,55h1v1h-1zM57,55h2v1h-2zM61,55h1v1h-1zM63,55h2v1h-2zM68,55h2v1h-2zM2,56h2v1h-2zM6,56h1v1h-1zM8,56h1v1h-1zM10,56h3v1h-3zM15,56h1v1h-1zM18,56h4v1h-4zM23,56h1v1h-1zM25,56h2v1h-2zM29,56h2v1h-2zM32,56h3v1h-3zM36,56h1v1h-1zM38,56h1v1h-1zM41,56h1v1h-1zM43,56h2v1h-2zM47,56h1v1h-1zM50,56h1v1h-1zM52,56h1v1h-1zM57,56h1v1h-1zM59,56h2v1h-2zM63,56h2v1h-2zM67,56h3v1h-3zM2,57h3v1h-3zM6,57h2v1h-2zM10,57h1v1h-1zM12,57h2v1h-2zM15,57h2v1h-2zM19,57h2v1h-2zM22,57h2v1h-2zM27,57h2v1h-2zM31,57h1v1h-1zM34,57h1v1h-1zM37,57h1v1h-1zM39,57h1v1h-1zM42,57h1v1h-1zM44,57h2v1h-2zM47,57h1v1h-1zM50,57h3v1h-3zM54,57h1v1h-1zM56,57h3v1h-3zM60,57h2v1h-2zM64,57h2v1h-2zM68,57h1v1h-1zM2,58h1v1h-1zM4,58h1v1h-1zM8,58h1v1h-1zM11,58h1v1h-1zM13,58h1v1h-1zM16,58h1v1h-1zM18,58h2v1h-2zM21,58h3v1h-3zM27,58h3v1h-3zM31,58h4v1h-4zM39,58h4v1h-4zM44,58h6v1h-6zM52,58h1v1h-1zM54,58h1v1h-1zM58,58h4v1h-4zM63,58h7v1h-7zM3,59h1v1h-1zM5,59h4v1h-4zM10,59h1v1h-1zM13,59h1v1h-1zM15,59h2v1h-2zM18,59h3v1h-3zM23,59h1v1h-1zM26,59h1v1h-1zM33,59h1v1h-1zM36,59h1v1h-1zM41,59h2v1h-2zM44,59h1v1h-1zM46,59h1v1h-1zM48,59h1v1h-1zM51,59h4v1h-4zM56,59h1v1h-1zM60,59h2v1h-2zM63,59h2v1h-2zM67,59h1v1h-1zM69,59h1v1h-1zM1,60h1v1h-1zM8,60h1v1h-1zM12,60h3v1h-3zM19,60h3v1h-3zM23,60h1v1h-1zM25,60h1v1h-1zM27,60h2v1h-2zM31,60h1v1h-1zM34,60h1v1h-1zM37,60h1v1h-1zM39,60h1v1h-1zM41,60h2v1h-2zM44,60h4v1h-4zM51,60h1v1h-1zM53,60h3v1h-3zM58,60h1v1h-1zM61,60h1v1h-1zM63,60h3v1h-3zM67,60h2v1h-2zM1,61h1v1h-1zM5,61h1v1h-1zM7,61h6v1h-6zM14,61h1v1h-1zM16,61h2v1h-2zM19,61h2v1h-2zM22,61h3v1h-3zM26,61h6v1h-6zM33,61h6v1h-6zM41,61h1v1h-1zM44,61h2v1h-2zM49,61h2v1h-2zM52,61h1v1h-1zM54,61h1v1h-1zM56,61h4v1h-4zM61,61h6v1h-6zM69,61h1v1h-1zM9,62h2v1h-2zM12,62h1v1h-1zM14,62h1v1h-1zM16,62h1v1h-1zM23,62h4v1h-4zM28,62h2v1h-2zM33,62h1v1h-1zM37,62h1v1h-1zM41,62h1v1h-1zM43,62h1v1h-1zM47,62h3v1h-3zM53,62h3v1h-3zM57,62h2v1h-2zM60,62h2v1h-2zM1,63h7v1h-7zM9,63h1v1h-1zM11,63h1v1h-1zM13,63h1v1h-1zM15,63h1v1h-1zM17,63h1v1h-1zM19,63h1v1h-1zM21,63h1v1h-1zM23,63h1v1h-1zM25,63h1v1h-1zM27,63h1v1h-1zM29,63h1v1h-1zM31,63h1v1h-1zM33,63h1v1h-1zM35,63h1v1h-1zM37,63h1v1h-1zM39,63h1v1h-1zM41,63h1v1h-1zM43,63h1v1h-1zM45,63h1v1h-1zM47,63h1v1h-1zM49,63h1v1h-1zM51,63h1v1h-1zM53,63h1v1h-1zM55,63h1v1h-1zM57,63h1v1h-1zM59,63h1v1h-1zM61,63h1v1h-1zM63,63h7v1h-7zM1,64h1v1h-1zM7,64h1v1h-1zM9,64h2v1h-2zM12,64h2v1h-2zM16,64h2v1h-2zM19,64h1v1h-1zM26,64h6v1h-6zM33,64h1v1h-1zM37,64h1v1h-1zM39,64h2v1h-2zM42,64h1v1h-1zM44,64h2v1h-2zM47,64h1v1h-1zM51,64h2v1h-2zM57,64h3v1h-3zM63,64h1v1h-1zM69,64h1v1h-1zM1,65h1v1h-1zM3,65h3v1h-3zM7,65h1v1h-1zM9,65h5v1h-5zM15,65h2v1h-2zM19,65h1v1h-1zM21,65h1v1h-1zM23,65h2v1h-2zM26,65h3v1h-3zM31,65h1v1h-1zM33,65h6v1h-6zM40,65h2v1h-2zM46,65h3v1h-3zM50,65h1v1h-1zM52,65h1v1h-1zM54,65h1v1h-1zM56,65h4v1h-4zM61,65h1v1h-1zM63,65h1v1h-1zM65,65h3v1h-3zM69,65h1v1h-1zM1,66h1v1h-1zM3,66h3v1h-3zM7,66h1v1h-1zM9,66h2v1h-2zM12,66h1v1h-1zM15,66h2v1h-2zM19,66h1v1h-1zM21,66h3v1h-3zM26,66h5v1h-5zM35,66h7v1h-7zM44,66h1v1h-1zM46,66h2v1h-2zM49,66h5v1h-5zM56,66h1v1h-1zM61,66h1v1h-1zM63,66h1v1h-1zM65,66h3v1h-3zM69,66h1v1h-1zM1,67h1v1h-1zM3,67h3v1h-3zM7,67h1v1h-1zM13,67h1v1h-1zM15,67h1v1h-1zM17,67h1v1h-1zM23,67h1v1h-1zM25,67h1v1h-1zM27,27h0v0zM27,67h2v1h-2zM30,67h2v1h-2zM34,67h2v1h-2zM37,67h1v1h-1zM40,67h4v1h-4zM47,67h2v1h-2zM50,67h1v1h-1zM52,67h1v1h-1zM54,67h6v1h-6zM63,67h1v1h-1zM65,67h3v1h-3zM69,67h1v1h-1zM1,68h1v1h-1zM7,68h1v1h-1zM10,68h3v1h-3zM15,68h1v1h-1zM17,68h3v1h-3zM21,68h1v1h-1zM23,68h2v1h-2zM28,68h2v1h-2zM31,68h1v1h-1zM34,68h1v1h-1zM37,68h3v1h-3zM41,68h2v1h-2zM44,68h1v1h-1zM47,68h2v1h-2zM57,68h2v1h-2zM63,68h1v1h-1zM69,68h1v1h-1zM1,69h7v1h-7zM9,69h3v1h-3zM15,69h1v1h-1zM17,69h2v1h-2zM20,69h2v1h-2zM26,69h1v1h-1zM28,69h1v1h-1zM30,69h1v1h-1zM32,69h1v1h-1zM37,69h3v1h-3zM41,69h3v1h-3zM46,69h3v1h-3zM50,69h1v1h-1zM52,69h2v1h-2zM55,69h3v1h-3zM59,69h3v1h-3zM63,69h7v1h-7z'
    },
    zalo: {
      size: 27,
      color: '#0068FF',
      path: 'M1,1h7v1h-7zM9,1h1v1h-1zM11,1h1v1h-1zM13,1h1v1h-1zM15,1h2v1h-2zM18,1h1v1h-1zM20,1h6v1h-6zM1,2h1v1h-1zM7,2h1v1h-1zM10,2h1v1h-1zM13,2h2v1h-2zM16,2h3v1h-3zM20,2h3v1h-3zM25,2h1v1h-1zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM9,3h2v1h-2zM14,3h2v1h-2zM17,3h1v1h-1zM22,3h2v1h-2zM25,3h1v1h-1zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM9,4h1v1h-1zM13,4h2v1h-2zM16,4h4v1h-4zM21,4h5v1h-5zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h1v1h-1zM12,5h1v1h-1zM16,5h6v1h-6zM23,5h1v1h-1zM25,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM9,6h1v1h-1zM12,6h1v1h-1zM15,6h1v1h-1zM17,6h1v1h-1zM21,6h2v1h-2zM25,6h1v1h-1zM1,7h7v1h-7zM10,7h4v1h-4zM17,7h1v1h-1zM19,7h1v1h-1zM21,7h1v1h-1zM23,7h3v1h-3zM9,8h1v1h-1zM11,8h1v1h-1zM14,8h4v1h-4zM21,8h2v1h-2zM1,9h1v1h-1zM3,9h3v1h-3zM7,9h3v1h-3zM11,9h1v1h-1zM13,9h2v1h-2zM17,9h5v1h-5zM23,9h1v1h-1zM1,10h1v1h-1zM3,10h4v1h-4zM8,10h4v1h-4zM13,10h2v1h-2zM16,10h2v1h-2zM19,10h3v1h-3zM25,10h1v1h-1zM1,11h1v1h-1zM5,11h1v1h-1zM7,11h1v1h-1zM9,11h3v1h-3zM14,11h5v1h-5zM20,11h3v1h-3zM24,11h2v1h-2zM1,12h2v1h-2zM5,12h1v1h-1zM8,12h2v1h-2zM11,12h1v1h-1zM13,12h1v1h-1zM15,12h1v1h-1zM17,12h1v1h-1zM20,12h1v1h-1zM22,12h1v1h-1zM24,12h1v1h-1zM1,13h1v1h-1zM3,13h5v1h-5zM9,13h3v1h-3zM15,13h2v1h-2zM18,13h4v1h-4zM23,13h3v1h-3zM5,14h1v1h-1zM8,14h1v1h-1zM10,14h1v1h-1zM12,14h3v1h-3zM16,14h4v1h-4zM21,14h1v1h-1zM25,14h1v1h-1zM1,15h2v1h-2zM4,15h4v1h-4zM9,15h1v1h-1zM11,15h3v1h-3zM16,15h2v1h-2zM19,15h1v1h-1zM21,15h2v1h-2zM24,15h2v1h-2zM1,16h3v1h-3zM5,16h2v1h-2zM10,16h2v1h-2zM14,16h2v1h-2zM20,16h1v1h-1zM24,16h1v1h-1zM1,17h1v1h-1zM3,17h5v1h-5zM10,17h1v1h-1zM13,17h1v1h-1zM15,17h1v1h-1zM19,17h5v1h-5zM9,18h2v1h-2zM12,18h4v1h-4zM17,18h1v1h-1zM1,19h7v1h-7zM9,19h1v1h-1zM11,19h1v1h-1zM13,19h1v1h-1zM15,19h1v1h-1zM17,19h1v1h-1zM19,19h7v1h-7zM1,20h1v1h-1zM7,20h1v1h-1zM9,20h2v1h-2zM14,20h1v1h-1zM16,20h2v1h-2zM19,20h1v1h-1zM25,20h1v1h-1zM1,21h1v1h-1zM3,21h3v1h-3zM7,21h1v1h-1zM9,21h1v1h-1zM11,21h1v1h-1zM15,21h2v1h-2zM19,21h1v1h-1zM21,21h3v1h-3zM25,21h1v1h-1zM1,22h1v1h-1zM3,22h3v1h-3zM7,22h1v1h-1zM9,22h5v1h-5zM15,22h3v1h-3zM19,22h1v1h-1zM21,22h3v1h-3zM25,22h1v1h-1zM1,23h1v1h-1zM3,23h3v1h-3zM7,23h1v1h-1zM9,23h2v1h-2zM16,23h1v1h-1zM19,23h1v1h-1zM21,23h3v1h-3zM25,23h1v1h-1zM1,24h1v1h-1zM7,24h1v1h-1zM10,24h1v1h-1zM13,24h1v1h-1zM16,24h1v1h-1zM19,24h1v1h-1zM25,24h1v1h-1zM1,25h7v1h-7zM11,25h4v1h-4zM19,25h7v1h-7z'
    },
    linkedin: {
      size: 35,
      color: '#0A66C2',
      path: 'M1,1h7v1h-7zM9,1h3v1h-3zM14,1h1v1h-1zM16,1h1v1h-1zM18,1h1v1h-1zM23,1h1v1h-1zM25,1h2v1h-2zM28,1h1v1h-1zM30,1h1v1h-1zM32,1h1v1h-1zM1,2h1v1h-1zM7,2h1v1h-1zM10,2h1v1h-1zM12,2h5v1h-5zM22,2h3v1h-3zM26,2h2v1h-2zM29,2h3v1h-3zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM9,3h2v1h-2zM13,3h1v1h-1zM15,3h4v1h-4zM21,3h8v1h-8zM30,3h1v1h-1zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM9,4h1v1h-1zM12,4h1v1h-1zM14,4h1v1h-1zM16,4h1v1h-1zM18,4h5v1h-5zM24,4h1v1h-1zM26,4h1v1h-1zM29,4h5v1h-5zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h2v1h-2zM13,5h1v1h-1zM15,5h1v1h-1zM17,5h1v1h-1zM23,5h1v1h-1zM25,5h6v1h-6zM33,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM9,6h1v1h-1zM12,6h2v1h-2zM15,6h2v1h-2zM18,6h2v1h-2zM21,6h5v1h-5zM29,6h4v1h-4zM1,7h7v1h-7zM11,7h3v1h-3zM16,7h3v1h-3zM22,7h1v1h-1zM24,7h2v1h-2zM27,7h1v1h-1zM29,7h1v1h-1zM31,7h2v1h-2zM9,8h1v1h-1zM14,8h1v1h-1zM17,8h6v1h-6zM24,8h2v1h-2zM29,8h1v1h-1zM31,8h1v1h-1zM33,8h1v1h-1zM1,9h1v1h-1zM5,9h3v1h-3zM9,9h2v1h-2zM12,9h2v1h-2zM18,9h2v1h-2zM23,9h1v1h-1zM25,9h5v1h-5zM1,10h1v1h-1zM3,10h1v1h-1zM6,10h1v1h-1zM9,10h1v1h-1zM11,10h5v1h-5zM17,10h1v1h-1zM20,10h1v1h-1zM22,10h3v1h-3zM26,10h2v1h-2zM30,10h4v1h-4zM1,11h1v1h-1zM3,11h2v1h-2zM6,11h4v1h-4zM11,11h1v1h-1zM13,11h3v1h-3zM26,11h1v1h-1zM32,11h1v1h-1zM1,12h4v1h-4zM8,12h1v1h-1zM10,12h2v1h-2zM13,12h2v1h-2zM16,12h3v1h-3zM20,12h1v1h-1zM23,12h3v1h-3zM27,12h1v1h-1zM30,12h1v1h-1zM33,12h1v1h-1zM1,13h2v1h-2zM4,13h2v1h-2zM7,13h2v1h-2zM10,13h3v1h-3zM14,13h1v1h-1zM19,13h2v1h-2zM29,13h2v1h-2zM1,14h2v1h-2zM5,14h1v1h-1zM11,14h1v1h-1zM13,14h2v1h-2zM17,14h1v1h-1zM22,14h1v1h-1zM24,14h1v1h-1zM27,14h6v1h-6zM2,15h7v1h-7zM12,15h1v1h-1zM16,15h1v1h-1zM19,15h1v1h-1zM21,15h1v1h-1zM26,15h4v1h-4zM31,15h2v1h-2zM1,16h1v1h-1zM3,16h1v1h-1zM8,16h1v1h-1zM13,16h2v1h-2zM19,16h4v1h-4zM24,16h5v1h-5zM30,16h2v1h-2zM33,16h1v1h-1zM5,17h4v1h-4zM11,17h6v1h-6zM18,17h1v1h-1zM20,17h1v1h-1zM23,17h4v1h-4zM28,17h2v1h-2zM33,17h1v1h-1zM2,18h2v1h-2zM8,18h1v1h-1zM11,18h1v1h-1zM13,18h4v1h-4zM20,18h3v1h-3zM25,18h7v1h-7zM7,19h1v1h-1zM10,19h1v1h-1zM13,19h2v1h-2zM16,19h3v1h-3zM21,19h1v1h-1zM23,19h1v1h-1zM26,19h2v1h-2zM30,19h3v1h-3zM1,20h3v1h-3zM5,20h2v1h-2zM8,20h2v1h-2zM11,20h1v1h-1zM14,20h1v1h-1zM16,20h1v1h-1zM18,20h2v1h-2zM24,20h2v1h-2zM27,20h1v1h-1zM30,20h1v1h-1zM32,20h2v1h-2zM3,21h2v1h-2zM6,21h2v1h-2zM9,21h2v1h-2zM12,21h1v1h-1zM15,21h1v1h-1zM17,21h1v1h-1zM20,21h1v1h-1zM23,21h2v1h-2zM26,21h1v1h-1zM28,21h3v1h-3zM32,21h2v1h-2zM2,22h3v1h-3zM6,22h1v1h-1zM9,22h2v1h-2zM12,22h3v1h-3zM17,22h8v1h-8zM26,22h1v1h-1zM29,22h3v1h-3zM33,22h1v1h-1zM1,23h2v1h-2zM4,23h2v1h-2zM7,23h2v1h-2zM11,23h1v1h-1zM14,23h5v1h-5zM23,23h1v1h-1zM25,23h2v1h-2zM29,23h1v1h-1zM31,23h1v1h-1zM2,24h2v1h-2zM8,24h2v1h-2zM12,24h1v1h-1zM14,24h2v1h-2zM17,24h4v1h-4zM22,24h1v1h-1zM24,24h1v1h-1zM27,24h2v1h-2zM30,24h2v1h-2zM33,24h1v1h-1zM1,25h1v1h-1zM3,25h5v1h-5zM10,25h1v1h-1zM12,25h1v1h-1zM14,25h2v1h-2zM18,25h1v1h-1zM20,25h1v1h-1zM23,25h1v1h-1zM25,25h1v1h-1zM27,25h5v1h-5zM9,26h1v1h-1zM11,26h1v1h-1zM17,26h1v1h-1zM20,26h5v1h-5zM1,27h7v1h-7zM9,27h1v1h-1zM11,27h1v1h-1zM13,27h1v1h-1zM15,27h1v1h-1zM17,27h1v1h-1zM19,27h1v1h-1zM21,27h1v1h-1zM23,27h1v1h-1zM25,27h1v1h-1zM27,27h7v1h-7zM1,28h1v1h-1zM7,28h1v1h-1zM9,28h1v1h-1zM11,28h2v1h-2zM14,28h1v1h-1zM18,28h3v1h-3zM22,28h1v1h-1zM25,28h1v1h-1zM27,28h1v1h-1zM33,28h1v1h-1zM1,29h1v1h-1zM3,29h3v1h-3zM7,29h1v1h-1zM9,29h2v1h-2zM15,29h3v1h-3zM21,29h1v1h-1zM23,29h2v1h-2zM27,29h1v1h-1zM29,29h3v1h-3zM33,29h1v1h-1zM1,30h1v1h-1zM3,30h3v1h-3zM7,30h1v1h-1zM9,30h3v1h-3zM13,30h1v1h-1zM16,30h1v1h-1zM19,30h2v1h-2zM24,30h2v1h-2zM27,30h1v1h-1zM29,30h3v1h-3zM33,30h1v1h-1zM1,31h1v1h-1zM3,31h3v1h-3zM7,31h1v1h-1zM9,31h2v1h-2zM15,31h1v1h-1zM20,31h4v1h-4zM27,31h1v1h-1zM29,31h3v1h-3zM33,31h1v1h-1zM1,32h1v1h-1zM7,32h1v1h-1zM11,32h1v1h-1zM16,32h1v1h-1zM19,32h1v1h-1zM22,32h1v1h-1zM25,32h1v1h-1zM27,32h1v1h-1zM33,32h1v1h-1zM1,33h7v1h-7zM11,33h3v1h-3zM15,33h1v1h-1zM17,33h1v1h-1zM19,33h4v1h-4zM24,33h1v1h-1zM27,33h7v1h-7z'
    }
  };

  const V4_FALLBACK_IMG =
    'data:image/svg+xml;charset=UTF-8,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">' +
        '<rect width="800" height="450" fill="#F8FAFC"/>' +
        '<rect x="36" y="36" width="728" height="378" fill="none" stroke="#E5E7EB" stroke-width="2"/>' +
        '<text x="400" y="218" text-anchor="middle" font-family="Georgia, serif" font-size="28" font-weight="700" fill="#0A3D7A">Bnews Fintech</text>' +
        '<text x="400" y="252" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#6B7280">Clean Institutional Intelligence</text>' +
      '</svg>'
    );

  const state = {
    data: null,
    activePage: 'today',
    activeCategory: 'ALL',
    searchTerm: '',
    activeChainIdx: 0,
    activeLayerIdx: 0,
    vcardTab: 'vcard',
    nlLoaded: false,
    newsById: {}
  };

  const INITIAL_PATH = window.location.pathname || '/';
  const CURRENT_DIR_BASE = (() => {
    if (window.location.protocol === 'file:') return './';
    const slashIdx = INITIAL_PATH.lastIndexOf('/');
    if (slashIdx >= 0 && /\.[a-z0-9]+$/i.test(INITIAL_PATH.slice(slashIdx + 1))) {
      return INITIAL_PATH.slice(0, slashIdx + 1);
    }
    return INITIAL_PATH.endsWith('/') ? INITIAL_PATH : `${INITIAL_PATH}/`;
  })();
  const IS_PREVIEW_SUBDIR = /\/preview\/$/i.test(CURRENT_DIR_BASE);
  const ROOT_ASSET_BASE =
    window.location.protocol === 'file:'
      ? (IS_PREVIEW_SUBDIR ? '../' : './')
      : (IS_PREVIEW_SUBDIR ? CURRENT_DIR_BASE.replace(/preview\/$/i, '') : CURRENT_DIR_BASE);
  const PORTFOLIO_HOME_URL =
    window.location.protocol === 'file:'
      ? (IS_PREVIEW_SUBDIR ? '../../index.html' : '../index.html')
      : (ROOT_ASSET_BASE.replace(/[^/]+\/$/, '') || '/');

  function getCleanPortalPath() {
    if (window.location.protocol === 'file:') return window.location.pathname;
    let p = INITIAL_PATH;
    if (p.endsWith('/index.html')) {
      p = p.slice(0, -'index.html'.length);
    } else if (p.endsWith('/magspread-preview.html')) {
      p = p.slice(0, -'magspread-preview.html'.length);
    }
    if (p.length > 1 && p.endsWith('/')) {
      p = p.slice(0, -1);
    }
    return p || '/';
  }

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function catLabel(rawCat) {
    return CAT_LABEL_MAP[rawCat] || rawCat || 'Tài chính';
  }

  function sourceLabel(item) {
    return item.originalSourceName || item.publisher || item.sourceName || 'Báo chí chính thống';
  }

  function extractTimeHM(item) {
    const iso = item.originalSourcePublishedAt || item.originalPublishedAt || '';
    const mIso = String(iso).match(/T(\d{2}:\d{2})/);
    if (mIso) return mIso[1];
    const pub = item.publisherPublishedAt || item.publicationTimestamp || '';
    const mPub = String(pub).match(/(\d{2}:\d{2})/);
    return mPub ? mPub[1] : '--:--';
  }

  function extractDateTimeReadable(item) {
    const pub = String(item.publisherPublishedAt || '').trim();
    const mPub = pub.match(/^(\d{2}\/\d{2}\/\d{4}\s+\d{2}:\d{2})/);
    if (mPub) return mPub[1];
    const iso = String(item.originalSourcePublishedAt || item.originalPublishedAt || '').trim();
    const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2})/);
    if (m) return `${m[3]}/${m[2]}/${m[1]} ${m[4]}`;
    return state.data?.editionDate || '';
  }

  function imgTag(src, alt, cls) {
    const safeSrc = src && /^https?:|^data:|^\./.test(src) ? src : V4_FALLBACK_IMG;
    return `<img src="${esc(safeSrc)}" alt="${esc(alt)}" class="${cls}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='${V4_FALLBACK_IMG}'">`;
  }

  // ─── DATA LOADER ──────────────────────────────────────────────────────────
  async function loadEditionData() {
    try {
      const resp = await fetch(`${ROOT_ASSET_BASE}edition-data.json?v=${Date.now()}`, { cache: 'no-store' });
      if (resp.ok) {
        return await resp.json();
      }
    } catch (_) {
      // Fall back silently to window.EDITION_DATA
    }
    return window.EDITION_DATA || null;
  }

  function updateSeoAndStructuredData() {
    const d = state.data;
    if (!d) return;
    const cs = d.editorialSections?.sec02_coverStory || {};
    const newsList = d.eligibleNewsList || [];
    const edMatch = String(d.editionNumber || '').match(/(\d+)/);
    const edLabel = edMatch ? `Ấn bản số ${edMatch[1]}` : 'Ấn bản mới nhất';
    const edDate = d.editionDate || '19/11/2026';
    const isoDate = (() => {
      const m = String(edDate).match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
      return m ? `${m[3]}-${m[2]}-${m[1]}` : '2026-11-19';
    })();
    const modifiedIso = d.editionCutoffAt || `${isoDate}T19:30:00+07:00`;
    const coverTitle = String(cs.editorialHeadline || '').trim();
    const seoTitle = IS_PREVIEW_SUBDIR
      ? `Bnews Fintech V4 Pilot — ${edLabel} (${edDate})`
      : `Bryan News | Fintech Intelligence — ${edLabel} (${edDate}) · ${newsList.length} Tin Kinh tế & Thanh toán số`;
    const seoDesc = coverTitle
      ? `Bryan News (${edLabel} · ${edDate}): ${coverTitle}. Tổng hợp ${newsList.length} sự kiện xác minh về Thanh toán số, Ngân hàng, Thị trường vốn, Doanh nghiệp, Vĩ mô và Bán lẻ.`
      : `Bryan News - Chuyên trang thông tin và phân tích ${newsList.length} sự kiện kinh tế vĩ mô, ngân hàng, thị trường tài chính và thanh toán số Việt Nam.`;

    document.title = seoTitle;

    const setMeta = (selector, content) => {
      if (!content) return;
      const el = document.querySelector(selector);
      if (el) el.setAttribute('content', content);
    };
    setMeta('meta[name="description"]', seoDesc);
    setMeta('meta[property="og:title"]', seoTitle);
    setMeta('meta[property="og:description"]', seoDesc);
    setMeta('meta[name="twitter:title"]', seoTitle);
    setMeta('meta[name="twitter:description"]', seoDesc);
    if (cs.leadArticle?.imageUrl) {
      setMeta('meta[property="og:image"]', cs.leadArticle.imageUrl);
      setMeta('meta[name="twitter:image"]', cs.leadArticle.imageUrl);
    }

    const schemaEl = document.getElementById('v4JsonLdSchema');
    if (schemaEl) {
      const portalUrl = 'https://bryanportfolio.io.vn/fintech-intelligence/';
      const topArticles = newsList.slice(0, 10).map((item, idx) => ({
        '@type': 'ListItem',
        position: idx + 1,
        url: item.canonicalUrl || item.sourceUrl || portalUrl,
        item: {
          '@type': 'NewsArticle',
          headline: item.headline || item.title || '',
          description: item.summary || '',
          datePublished: item.originalSourcePublishedAt || item.originalPublishedAt || modifiedIso,
          articleSection: catLabel(item.category),
          image: item.imageUrl || 'https://bryanportfolio.io.vn/fintech-intelligence/bnews-logo-light.png',
          url: item.canonicalUrl || item.sourceUrl || portalUrl,
          publisher: {
            '@type': 'Organization',
            name: sourceLabel(item)
          }
        }
      }));

      const ldObj = {
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': ['NewsMediaOrganization', 'WebSite'],
            '@id': `${portalUrl}#website`,
            name: 'Bryan News | Fintech Intelligence',
            alternateName: ['Bryan News', 'Bnews Fintech', 'Fintech Intelligence VN'],
            url: portalUrl,
            description: seoDesc,
            inLanguage: 'vi-VN',
            logo: {
              '@type': 'ImageObject',
              url: 'https://bryanportfolio.io.vn/fintech-intelligence/bnews-logo-light.png',
              width: 1200,
              height: 630
            },
            publisher: {
              '@type': 'Person',
              name: 'Nguyễn Huỳnh Quang Trí (Bryan Nguyen)',
              jobTitle: 'Enterprise B2B & Fintech Product Specialist',
              url: 'https://bryanportfolio.io.vn/',
              sameAs: [
                'https://www.linkedin.com/in/bryan-nguyen-796a7b1ab/',
                'https://zalo.me/0838673639',
                'https://www.facebook.com/Tori1005'
              ]
            },
            potentialAction: {
              '@type': 'SearchAction',
              target: {
                '@type': 'EntryPoint',
                urlTemplate: `${portalUrl}?q={search_term_string}`
              },
              'query-input': 'required name=search_term_string'
            }
          },
          {
            '@type': 'CollectionPage',
            '@id': `${portalUrl}#webpage`,
            url: portalUrl,
            name: seoTitle,
            description: seoDesc,
            inLanguage: 'vi-VN',
            datePublished: `${isoDate}T09:00:00+07:00`,
            dateModified: modifiedIso,
            isPartOf: { '@id': `${portalUrl}#website` },
            breadcrumb: { '@id': `${portalUrl}#breadcrumb` }
          },
          {
            '@type': 'BreadcrumbList',
            '@id': `${portalUrl}#breadcrumb`,
            itemListElement: [
              { '@type': 'ListItem', position: 1, name: 'Bryan Portfolio', item: 'https://bryanportfolio.io.vn/' },
              { '@type': 'ListItem', position: 2, name: 'Bryan News | Fintech Intelligence', item: portalUrl }
            ]
          },
          {
            '@type': 'NewsArticle',
            '@id': `${portalUrl}#cover-story`,
            headline: coverTitle || seoTitle,
            description: cs.editorialSubheadline || cs.dek || seoDesc,
            image: cs.leadArticle?.imageUrl || 'https://bryanportfolio.io.vn/fintech-intelligence/bnews-logo-light.png',
            datePublished: `${isoDate}T09:00:00+07:00`,
            dateModified: modifiedIso,
            author: { '@type': 'Person', name: 'Nguyễn Huỳnh Quang Trí (Bryan Nguyen)', url: 'https://bryanportfolio.io.vn/' },
            publisher: { '@id': `${portalUrl}#website` },
            mainEntityOfPage: { '@id': `${portalUrl}#webpage` }
          },
          {
            '@type': 'ItemList',
            '@id': `${portalUrl}#edition-articles`,
            name: `Danh sách tin nổi bật ${edLabel} (${edDate})`,
            numberOfItems: newsList.length,
            itemListElement: topArticles
          }
        ]
      };
      schemaEl.textContent = JSON.stringify(ldObj);
    }
  }

  // ─── HEADER & MARKET PULSE (44PX) ─────────────────────────────────────────
  function renderMasthead() {
    const d = state.data;
    const dateEl = $('#v4Date');
    const edEl = $('#v4EditionLabel');
    const drawerBadgeEl = $('#v4DrawerEditionBadge');
    const footerMetaEl = $('#v4FooterEditionMeta');

    if (dateEl && (d.dayOfWeek || d.editionDate)) {
      const dow = String(d.dayOfWeek || '')
        .toLowerCase()
        .replace(/(^|\s)\S/g, (ch) => ch.toUpperCase());
      dateEl.textContent = `${dow ? dow + ', ' : ''}${d.editionDate || ''}`;
    }
    if (edEl && d.editionNumber) {
      const rawEd = String(d.editionNumber);
      const mNum = rawEd.match(/(\d+)/);
      edEl.textContent = mNum ? `Ấn bản số ${mNum[1]}` : rawEd;
      if (drawerBadgeEl) {
        const cleanBadge = rawEd
          .replace(/ẤN BẢN SỐ/gi, 'Ấn bản số')
          .replace(/PHIÊN CHIỀU/gi, 'Phiên chiều')
          .replace(/PHIÊN SÁNG/gi, 'Phiên sáng');
        drawerBadgeEl.textContent = cleanBadge;
      }
    }
    if (footerMetaEl && d.editionId) {
      footerMetaEl.textContent = `${d.editionId} · ${d.editionDate || ''} · Institutional V4.0`;
    }
  }

  function formatPulseParts(m) {
    const sl = String(m.shortLabel || m.label || '').toUpperCase();
    const rawVal = String(m.value || '');
    const rawDelta = String(m.compactDelta || '');

    let shortName = m.shortLabel || m.label || 'Chỉ số';
    let cleanVal = rawVal;
    let cleanDelta = '';
    let tone = 'is-neutral';

    if (sl.includes('USD')) {
      shortName = 'USD/VND';
      cleanVal = rawVal.replace(/\s*VND\/USD/i, '').trim();
      const mDelta = rawDelta.match(/^([+-]?\d[\d.,]*đ)/i);
      cleanDelta = mDelta ? `(${mDelta[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = m.status === 'negative' ? 'is-down' : m.status === 'positive' ? 'is-up' : 'is-neutral';
    } else if (sl.includes('LÃI SUẤT')) {
      shortName = 'Lãi suất 12T';
      cleanVal = rawVal.replace(/\s*%\/năm/i, '%').replace(/\s+%/g, '%').trim();
      cleanDelta = '';
      tone = 'is-neutral';
    } else if (sl.includes('VN-INDEX')) {
      shortName = 'VN-Index';
      cleanVal = rawVal.replace(/\s*Điểm/i, '').trim();
      const mPct = rawDelta.match(/\(([+-]?[\d.,]+%)\)/);
      cleanDelta = mPct ? `(${mPct[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = cleanDelta.includes('-') || m.status === 'negative' ? 'is-down' : 'is-up';
    } else if (sl.includes('KHÁCH')) {
      shortName = 'Khách QT';
      cleanVal = rawVal.replace(/\s*Triệu lượt/i, 'M').replace(/\s+M$/i, 'M').trim();
      const mYoy = rawDelta.match(/([+-]?[\d.,]+%)/);
      cleanDelta = mYoy ? `(${mYoy[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = m.status === 'positive' ? 'is-up' : m.status === 'negative' ? 'is-down' : 'is-neutral';
    }

    return { shortName, cleanVal, cleanDelta, tone };
  }

  function renderPulseStrip() {
    const track = $('#v4PulseTrack');
    const items = state.data.marketPulseSnapshot || [];
    if (!track || !items.length) return;

    track.innerHTML = items
      .map((m, idx) => {
        const p = formatPulseParts(m);
        return `
          <button type="button" class="v4-pulse-item" data-mp-idx="${idx}" title="Bấm xem nguồn đối soát ${esc(p.shortName)}">
            <span class="v4-pulse-name">${esc(p.shortName)}</span>
            <span class="v4-pulse-val">${esc(p.cleanVal)}</span>
            ${p.cleanDelta ? `<span class="v4-pulse-delta ${p.tone}">${esc(p.cleanDelta)}</span>` : ''}
          </button>
        `;
      })
      .join('');

    track.querySelectorAll('.v4-pulse-item').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.dataset.mpIdx);
        openMarketPulseDrawer(items[idx]);
      });
    });
  }

  // ─── B1. TRANG NHẤT 3 CỘT (25% | 50% | 25%) ─────────────────────────────────
  function parseSynthesisPoints(synthStr) {
    if (!synthStr) return [];
    const cleaned = String(synthStr)
      .replace(/^Toàn cảnh phiên[^:]*:\s*/i, '')
      .trim();
    const matches = cleaned.match(/\(\d\)\s*[^;]+(?:;|$)/g);
    if (!matches || !matches.length) {
      return [{ num: '01', title: 'Đúc kết thị trường', body: cleaned }];
    }
    return matches.slice(0, 4).map((rawItem, idx) => {
      const noPrefix = rawItem.replace(/^\(\d\)\s*/, '').replace(/;$/, '').trim();
      const colonIdx = noPrefix.indexOf(':');
      if (colonIdx > 0 && colonIdx < 80) {
        return {
          num: `0${idx + 1}`,
          title: noPrefix.slice(0, colonIdx).trim(),
          body: noPrefix.slice(colonIdx + 1).trim()
        };
      }
      return {
        num: `0${idx + 1}`,
        title: `Mạch chuyển động ${idx + 1}`,
        body: noPrefix
      };
    });
  }

  function renderFrontPage() {
    const cs = state.data.editorialSections?.sec02_coverStory || {};
    const newsList = state.data.eligibleNewsList || [];
    const leadId = cs.leadArticle?.eventId || newsList[0]?.eventId;
    const leadItem = state.newsById[leadId] || cs.leadArticle || newsList[0];

    // Cột trái (25%): Đúc kết 4 mạch phiên 01 -> 04
    const synthCol = $('#v4SynthesisCol');
    if (synthCol) {
      const points = parseSynthesisPoints(cs.editorialSynthesis);
      synthCol.innerHTML = `
        <div class="v4-col-label">
          <span>Đúc kết 4 mạch phiên</span>
          <span class="v4-col-label-sub">${newsList.length} tin</span>
        </div>
        <div class="v4-synth-list">
          ${points
            .map(
              (pt) => `
            <div class="v4-synth-item">
              <div class="v4-synth-num">${esc(pt.num)}</div>
              <div>
                <h3 class="v4-synth-title">${esc(pt.title)}</h3>
                <p class="v4-synth-desc">${esc(pt.body)}</p>
              </div>
            </div>
          `
            )
            .join('')}
        </div>
      `;
    }

    // Cột giữa (50%): Bài đinh trang nhất (không có nhãn XÁC MINH 100%)
    const coverCol = $('#v4CoverCol');
    if (coverCol && leadItem) {
      const coverTitle = cs.editorialHeadline || leadItem.headline || leadItem.title;
      const coverSapo = cs.editorialSubheadline || leadItem.summary || cs.dek || '';
      const coverImg = leadItem.imageUrl || cs.imageUrl;
      const categoryTxt = catLabel(leadItem.category || 'Ngân hàng');
      const srcTxt = sourceLabel(leadItem);
      const timeTxt = extractDateTimeReadable(leadItem);

      coverCol.innerHTML = `
        <article class="v4-cover-card">
          <button type="button" class="v4-cover-img-btn" data-open-event="${esc(leadItem.eventId)}" aria-label="Đọc bài đinh: ${esc(coverTitle)}">
            ${imgTag(coverImg, coverTitle, 'v4-cover-img')}
          </button>
          <div class="v4-cover-kicker">
            <span class="v4-crimson-tag">${esc(categoryTxt)} · Tiêu điểm</span>
          </div>
          <h1 class="v4-cover-headline" data-open-event="${esc(leadItem.eventId)}">${esc(coverTitle)}</h1>
          <p class="v4-cover-sapo">${esc(coverSapo)}</p>
          <div class="v4-article-meta">
            <span>${esc(srcTxt)}</span>
            <span aria-hidden="true">·</span>
            <span class="v4-mono-time">${esc(timeTxt)}</span>
            <button type="button" class="v4-read-inline-btn" data-open-event="${esc(leadItem.eventId)}">Đọc phân tích chi tiết &rarr;</button>
          </div>
        </article>
      `;
    }

    // Cột phải (25%): Dòng tin mới 0-24h (6 tin mới nhất, không trùng bài đinh)
    const feedCol = $('#v4LatestFeedCol');
    if (feedCol) {
      const latestSix = newsList
        .filter((n) => n.eventId !== leadId)
        .slice()
        .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''))
        .slice(0, 6);

      feedCol.innerHTML = `
        <div class="v4-col-label">
          <span>Dòng tin mới 0–24h</span>
          <span class="v4-col-label-sub">Quét nhanh</span>
        </div>
        <div class="v4-feed-list">
          ${latestSix
            .map(
              (item) => `
            <article class="v4-feed-item" data-open-event="${esc(item.eventId)}">
              <div class="v4-feed-meta">
                <span class="v4-crimson-tag">${esc(catLabel(item.category))}</span>
                <span class="v4-mono-time">${esc(extractTimeHM(item))}</span>
              </div>
              <h3 class="v4-feed-title">${esc(item.headline || item.title)}</h3>
            </article>
          `
            )
            .join('')}
        </div>
      `;
    }
  }

  // ─── B2. 6 CHUYÊN MỤC TIN TỨC (KHÔNG TRÙNG BÀI ĐINH) ───────────────────────
  function renderCategoryClusters() {
    const mount = $('#v4CategoriesMount');
    if (!mount) return;

    const cs = state.data.editorialSections?.sec02_coverStory || {};
    const leadId = cs.leadArticle?.eventId;
    const newsList = (state.data.eligibleNewsList || []).filter((n) => n.eventId !== leadId);

    const grouped = CATEGORIES.map((cat) => {
      const items = newsList
        .filter((n) => n.category === cat.key)
        .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''));
      return { ...cat, items };
    }).filter((g) => g.items.length > 0);

    const richGroups = grouped.filter((g) => g.items.length >= 4);
    const sparseGroups = grouped.filter((g) => g.items.length < 4);

    let html = richGroups
      .map((g) => {
        const first = g.items[0];
        const nextFour = g.items.slice(1, 5);
        return `
        <div class="v4-cat-cluster" data-cat-cluster="${esc(g.key)}">
          <div class="v4-cat-cluster-head">
            <h2 class="v4-cat-heading">${esc(g.label)}</h2>
            <div class="v4-cat-actions">
              <span class="v4-cat-count">${g.items.length} bản tin</span>
              <button type="button" class="v4-cat-more-btn" data-filter-cat="${esc(g.key)}">Xem tất cả ${g.items.length} tin &rarr;</button>
            </div>
          </div>

          <div class="v4-cat-rich-grid">
            <article class="v4-cat-lead" data-open-event="${esc(first.eventId)}">
              <div class="v4-cat-lead-media">${imgTag(first.imageUrl, first.headline, 'v4-cat-lead-img')}</div>
              <div class="v4-cat-lead-body">
                <h3 class="v4-cat-lead-title">${esc(first.headline || first.title)}</h3>
                <p class="v4-cat-lead-sapo">${esc(first.summary || '')}</p>
                <div class="v4-article-meta">
                  <span>${esc(sourceLabel(first))}</span>
                  <span aria-hidden="true">·</span>
                  <span class="v4-mono-time">${esc(extractTimeHM(first))}</span>
                </div>
              </div>
            </article>

            <div class="v4-cat-stack">
              ${nextFour
                .map(
                  (it) => `
                <article class="v4-cat-stack-item" data-open-event="${esc(it.eventId)}">
                  <div class="v4-cat-stack-thumb">${imgTag(it.imageUrl, it.headline, 'v4-thumb-img')}</div>
                  <div class="v4-cat-stack-body">
                    <h4 class="v4-cat-stack-title">${esc(it.headline || it.title)}</h4>
                    <div class="v4-article-meta">
                      <span>${esc(sourceLabel(it))}</span>
                      <span aria-hidden="true">·</span>
                      <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                    </div>
                  </div>
                </article>
              `
                )
                .join('')}
            </div>
          </div>
        </div>
      `;
      })
      .join('');

    if (sparseGroups.length) {
      html += `
        <div class="v4-sparse-grid">
          ${sparseGroups
            .map((g) => {
              const first = g.items[0];
              const rest = g.items.slice(1);
              return `
              <div class="v4-sparse-cluster" data-cat-cluster="${esc(g.key)}">
                <div class="v4-cat-cluster-head">
                  <h2 class="v4-cat-heading">${esc(g.label)}</h2>
                  <button type="button" class="v4-cat-more-btn" data-filter-cat="${esc(g.key)}">Mở rộng &rarr;</button>
                </div>
                <article class="v4-sparse-card" data-open-event="${esc(first.eventId)}">
                  <div class="v4-thumb-wrap">${imgTag(first.imageUrl, first.headline, 'v4-thumb-img')}</div>
                  <div>
                    <h3 class="v4-sparse-title">${esc(first.headline || first.title)}</h3>
                    <p class="v4-cat-lead-sapo">${esc(first.summary || '')}</p>
                    <div class="v4-article-meta">
                      <span>${esc(sourceLabel(first))}</span>
                      <span aria-hidden="true">·</span>
                      <span class="v4-mono-time">${esc(extractTimeHM(first))}</span>
                    </div>
                  </div>
                </article>
                ${
                  rest.length
                    ? `<div class="v4-cat-stack" style="border-left:none; padding-left:0; margin-top:12px;">
                        ${rest
                          .map(
                            (it) => `
                          <article class="v4-cat-stack-item" data-open-event="${esc(it.eventId)}">
                            <div class="v4-cat-stack-thumb">${imgTag(it.imageUrl, it.headline, 'v4-thumb-img')}</div>
                            <div class="v4-cat-stack-body">
                              <h4 class="v4-cat-stack-title">${esc(it.headline || it.title)}</h4>
                              <div class="v4-article-meta">
                                <span>${esc(sourceLabel(it))}</span>
                                <span aria-hidden="true">·</span>
                                <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                              </div>
                            </div>
                          </article>
                        `
                          )
                          .join('')}
                      </div>`
                    : ''
                }
              </div>
            `;
            })
            .join('')}
        </div>
      `;
    }

    mount.innerHTML = html;
  }

  // ─── C1. CHUỖI TRUYỀN DẪN VĨ MÔ -> VI MÔ (CHẤT TẠP CHÍ 7 BƯỚC NGANG) ────────
  function renderMacroMicro() {
    const chains = state.data.editorialSections?.sec06_macroToMicro?.chains || [];
    const tabsEl = $('#v4ChainTabs');
    const headEl = $('#v4ChainHeader');
    const stepBarEl = $('#v4StepBar');
    const stepContentEl = $('#v4StepContent');
    if (!chains.length || !tabsEl || !headEl || !stepBarEl || !stepContentEl) return;

    if (state.activeChainIdx >= chains.length) state.activeChainIdx = 0;
    const activeChain = chains[state.activeChainIdx];
    const layers = activeChain.layers || [];
    if (state.activeLayerIdx >= layers.length) state.activeLayerIdx = 0;
    const activeLayer = layers[state.activeLayerIdx] || {};

    tabsEl.innerHTML = chains
      .map((ch, idx) => {
        const shortT = String(ch.title || ch.chainTitle || `Chuỗi ${idx + 1}`)
          .replace(/^Chuỗi truyền dẫn vĩ mô\s*[—-]\s*vi mô:\s*/i, '');
        return `
          <button type="button" class="v4-chain-tab ${idx === state.activeChainIdx ? 'active' : ''}" data-chain-idx="${idx}">
            0${idx + 1} · ${esc(shortT)}
          </button>
        `;
      })
      .join('');

    headEl.innerHTML = `
      <h3 class="v4-chain-title">${esc(activeChain.title || activeChain.chainTitle)}</h3>
      <p class="v4-chain-thesis">${esc(activeChain.coreThesis || activeChain.macroDriver || '')}</p>
    `;

    stepBarEl.innerHTML = layers
      .map((ly, idx) => {
        const stepNum = String(ly.levelNumber || idx + 1).padStart(2, '0');
        const shortLayer = String(ly.levelName || ly.layerName || ly.title || '')
          .replace(/^Tầng\s*\d+:\s*/i, '');
        return `
          <button type="button" class="v4-step-btn ${idx === state.activeLayerIdx ? 'active' : ''}" data-layer-idx="${idx}" role="tab" aria-selected="${idx === state.activeLayerIdx}">
            <span class="v4-step-num">${esc(stepNum)}</span>
            <span class="v4-step-label">${esc(shortLayer)}</span>
          </button>
        `;
      })
      .join('');

    const relEvents = (activeLayer.eventIds || [])
      .map((eid) => state.newsById[eid])
      .filter(Boolean);

    const stepNumStr = String(activeLayer.levelNumber || state.activeLayerIdx + 1).padStart(2, '0');
    const stepBadge = activeLayer.badge === 'INFERENCE' ? 'SUY LUẬN HỆ THỐNG' : 'SỰ KIỆN XÁC MINH';

    stepContentEl.innerHTML = `
      <div>
        <div class="v4-step-kicker">
          <span class="v4-step-badge">${esc(stepBadge)}</span>
          <span class="v4-step-layer-name">${esc(activeLayer.levelName || `Tầng ${stepNumStr}`)}</span>
        </div>
        <h4 class="v4-step-heading">${esc(activeLayer.title || '')}</h4>
        <p class="v4-step-desc">${esc(activeLayer.content || activeLayer.description || '')}</p>
        <div class="v4-step-pager">
          <button type="button" class="v4-step-pager-btn" id="v4PrevStepBtn" ${state.activeLayerIdx === 0 ? 'disabled' : ''}>&larr; Tầng trước</button>
          <button type="button" class="v4-step-pager-btn" id="v4NextStepBtn" ${state.activeLayerIdx >= layers.length - 1 ? 'disabled' : ''}>Tầng tiếp theo &rarr;</button>
        </div>
      </div>

      <aside class="v4-step-side">
        <div class="v4-step-side-label">Động lực vĩ mô dẫn dắt</div>
        <p class="v4-step-driver">${esc(activeChain.macroDriver || activeChain.coreThesis || '')}</p>

        <div class="v4-step-side-label">Tin tức liên đới ở tầng này (${relEvents.length})</div>
        <div class="v4-step-events">
          ${
            relEvents.length
              ? relEvents
                  .map(
                    (ev) => `
                  <button type="button" class="v4-step-event-link" data-open-event="${esc(ev.eventId)}">
                    <span class="v4-step-event-title">${esc(ev.headline || ev.title)}</span>
                    <span class="v4-step-event-src">${esc(sourceLabel(ev))} · ${esc(extractTimeHM(ev))}</span>
                  </button>
                `
                  )
                  .join('')
              : '<span class="v4-step-event-src">Tầng phân tích tổng hợp xuyên suốt mạch dữ kiện phiên.</span>'
          }
        </div>
      </aside>
    `;

    tabsEl.querySelectorAll('.v4-chain-tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeChainIdx = Number(btn.dataset.chainIdx);
        state.activeLayerIdx = 0;
        renderMacroMicro();
      });
    });

    stepBarEl.querySelectorAll('.v4-step-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeLayerIdx = Number(btn.dataset.layerIdx);
        renderMacroMicro();
      });
    });

    const prevBtn = $('#v4PrevStepBtn');
    const nextBtn = $('#v4NextStepBtn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (state.activeLayerIdx > 0) {
          state.activeLayerIdx -= 1;
          renderMacroMicro();
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (state.activeLayerIdx < layers.length - 1) {
          state.activeLayerIdx += 1;
          renderMacroMicro();
        }
      });
    }
  }

  // ─── C2. GÓC CHUYÊN MÔN FINTECH (3 CỘT + PLAYBOOK 2 CỘT + TỪ ĐIỂN PHẲNG) ────
  function renderFintechCorner() {
    const elSec = state.data.editorialSections?.sec08_expertLearning || {};
    const lessons = elSec.lessons || [];
    const frameworks = elSec.frameworks || [];
    const playbooks = elSec.salesPlaybook || [];
    const glossary = elSec.fintechGlossary || [];

    // 1. Lưới 3 cột không viền khung (6 mục: 4 lessons + 2 frameworks = 2 hàng x 3 cột đầy đặn)
    const gridEl = $('#v4FintechGrid');
    if (gridEl) {
      const mergedItems = [
        ...lessons.map((l, idx) => ({
          kind: 'lesson',
          idx,
          kicker: l.concept || 'Kiến thức Fintech',
          title: l.title || l.topic,
          desc: l.simpleExplanation || l.newsGrounding || '',
          payload: l
        })),
        ...frameworks.map((fw, idx) => ({
          kind: 'framework',
          idx,
          kicker: 'Khung kiến trúc chuyển dịch',
          title: String(fw.frameworkTitle || '').replace(/^Framework\s*\d+:\s*/i, ''),
          desc: `${fw.step1 || ''} ${fw.step2 || ''}`.trim(),
          payload: fw
        }))
      ];

      gridEl.innerHTML = mergedItems
        .map(
          (item, i) => `
          <article class="v4-fintech-card" data-fintech-idx="${i}">
            <div class="v4-fintech-card-cat">${esc(item.kicker)}</div>
            <h3 class="v4-fintech-card-title">${esc(item.title)}</h3>
            <p class="v4-fintech-card-desc">${esc(item.desc)}</p>
            <span class="v4-fintech-card-cta">Đọc chuyên đề &rarr;</span>
          </article>
        `
        )
        .join('');

      gridEl.querySelectorAll('.v4-fintech-card').forEach((card) => {
        card.addEventListener('click', () => {
          const item = mergedItems[Number(card.dataset.fintechIdx)];
          openFintechItemDrawer(item);
        });
      });
    }

    // 2. Playbook 2 cột cân đối
    const pbGrid = $('#v4PlaybookGrid');
    if (pbGrid) {
      pbGrid.innerHTML = playbooks
        .map(
          (pb, idx) => `
          <article class="v4-playbook-card" data-playbook-idx="${idx}">
            <div class="v4-fintech-card-cat">Playbook 0${idx + 1}</div>
            <h4 class="v4-playbook-title">${esc(pb.title)}</h4>
            <p class="v4-playbook-pitch">${esc(pb.pitch)}</p>
            <div class="v4-playbook-meta">Đối tượng: ${esc(pb.target)}</div>
          </article>
        `
        )
        .join('');

      pbGrid.querySelectorAll('.v4-playbook-card').forEach((card) => {
        card.addEventListener('click', () => {
          openPlaybookDrawer(playbooks[Number(card.dataset.playbookIdx)]);
        });
      });
    }

    // 3. Từ điển 2 cột phẳng (table)
    const glBody = $('#v4GlossaryBody');
    if (glBody) {
      glBody.innerHTML = glossary
        .map(
          (g) => `
          <tr>
            <td class="v4-glossary-term">${esc(g.term)}</td>
            <td>${esc(g.definition)}</td>
          </tr>
        `
        )
        .join('');
    }
  }

  // ─── TRANG 04: TÍN HIỆU & CƠ HỘI B2B ───────────────────────────────────────
  function renderB2BPage() {
    const es = state.data.editorialSections || {};
    const signals = es.sec04b_decisionBrief?.signals || [];
    const opps = es.sec07_paymentRadar?.opportunities || [];
    const watchlist = es.sec08b_watchlist?.items || es.sec08b_watchlist?.watchlistItems || [];

    const dbMount = $('#v4DecisionBriefMount');
    if (dbMount) {
      dbMount.innerHTML = signals
        .map((sig, idx) => {
          const sigId = sig.signalId || `DECISION-0${idx + 1}`;
          const segs = (sig.relevantMerchantSegments || []).slice(0, 4);
          const sols = (sig.potentialPaymentSolutions || []).slice(0, 2);
          return `
            <article class="v4-b2b-card is-clickable" data-open-signal="${esc(sigId)}">
              <div class="v4-b2b-card-top">
                <span class="v4-crimson-tag">${esc(sig.categoryBadge || 'TÍN HIỆU ĐIỀU HÀNH')}</span>
                <span class="v4-b2b-pill">${esc(sigId)}</span>
              </div>
              <h3 class="v4-b2b-title">${esc(sig.signalTitle || '')}</h3>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Diễn biến thị trường</div>
                <p class="v4-b2b-text">${esc(sig.whatHappened || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Cơ hội ứng dụng B2B</div>
                <p class="v4-b2b-text">${esc(sig.whatItMeansForMyWork || sig.proposedNextAction || '')}</p>
              </div>
              ${
                segs.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Phân khúc ưu tiên</div>
                      <div class="v4-b2b-tags">${segs.map((s) => `<span class="v4-b2b-tag">${esc(s)}</span>`).join('')}</div>
                    </div>`
                  : ''
              }
              ${
                sols.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Giải pháp đối ứng</div>
                      <p class="v4-b2b-text">${sols.map((s) => `<strong>${esc(s.solutionName)}</strong>: ${esc(s.capabilityNote)}`).join('<br>')}</p>
                    </div>`
                  : ''
              }
              <button type="button" class="v4-b2b-more-btn" data-open-signal="${esc(sigId)}">Xem phân tích điều hành &amp; nguồn đối soát &rarr;</button>
            </article>
          `;
        })
        .join('');
    }

    const radarMount = $('#v4PaymentRadarMount');
    if (radarMount) {
      radarMount.innerHTML = opps
        .map((op) => {
          const rels = (op.relevantEventIds || op.originEventIds || [])
            .map((eid) => state.newsById[eid])
            .filter(Boolean);
          return `
            <article class="v4-b2b-card">
              <div class="v4-b2b-card-top">
                <span class="v4-crimson-tag">${esc(op.merchantSegment || 'B2B PAYMENT RADAR')}</span>
                <span class="v4-b2b-pill">${esc(op.opportunityId || 'RADAR')} · ${esc(op.priority || 'P1')}</span>
              </div>
              <h3 class="v4-b2b-title">${esc(op.title || op.opportunityTitle || '')}</h3>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Điểm nghẽn thanh toán</div>
                <p class="v4-b2b-text">${esc(op.paymentPainPoint || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Giải pháp &amp; Giá trị thương mại</div>
                <p class="v4-b2b-text">${esc(op.paymentSolution || '')} ${esc(op.commercialRationale || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Hành động đề xuất</div>
                <p class="v4-b2b-text"><strong>${esc(op.proposedBDAction || '')}</strong></p>
              </div>
              ${
                rels.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Tin tức nền tảng (${rels.length})</div>
                      <div class="v4-b2b-tags">
                        ${rels
                          .map(
                            (ev) => `<button type="button" class="v4-b2b-tag" style="cursor:pointer;" data-open-event="${esc(ev.eventId)}">${esc(ev.eventId)} · ${esc((ev.headline || '').slice(0, 56))}...</button>`
                          )
                          .join('')}
                      </div>
                    </div>`
                  : ''
              }
            </article>
          `;
        })
        .join('');
    }

    const wlMount = $('#v4WatchlistMount');
    if (wlMount) {
      wlMount.innerHTML = watchlist
        .map(
          (wl, idx) => `
          <article class="v4-b2b-card">
            <div class="v4-b2b-card-top">
              <span class="v4-crimson-tag">${esc(wl.category || 'GIÁM SÁT VĨ MÔ')}</span>
              <span class="v4-b2b-pill">${esc(wl.watchlistId || `WL-0${idx + 1}`)} · ${esc(wl.impactLevel || 'HIGH')}</span>
            </div>
            <h3 class="v4-b2b-title">${esc(wl.itemTitle || '')}</h3>
            <div class="v4-b2b-row">
              <div class="v4-b2b-label">Chỉ báo theo dõi (${esc(wl.observationHorizon || '7 ngày tới')})</div>
              <p class="v4-b2b-text">${esc(wl.signalTracked || wl.description || '')}</p>
            </div>
            <div class="v4-b2b-row">
              <div class="v4-b2b-label">Ngưỡng kích hoạt &amp; Hành động</div>
              <p class="v4-b2b-text"><strong>Ngưỡng:</strong> ${esc(wl.threshold || wl.conditionChangingAssessment || '')}<br><strong>Đề xuất:</strong> ${esc(wl.possibleAction || '')}</p>
            </div>
          </article>
        `
        )
        .join('');
    }
  }

  // ─── CHUYỂN TRANG ĐIỀU HÀNH (01 -> 04) ──────────────────────────────────────
  function loadNewsletterPreview() {
    if (state.nlLoaded) return;
    const mount = $('#v4NlPreviewMount');
    if (!mount) return;
    state.nlLoaded = true;
    const nlUrl = `${CURRENT_DIR_BASE}newsletter-preview.html?v=${Date.now()}`;
    mount.innerHTML = `<iframe src="${nlUrl}" class="v4-nl-iframe" title="Bản tin Bnews mới nhất"></iframe>`;
    const ifr = mount.querySelector('iframe');
    if (ifr) {
      ifr.addEventListener('load', () => {
        try {
          const h = ifr.contentDocument?.documentElement?.scrollHeight;
          if (h && h > 400) ifr.style.height = `${h + 24}px`;
        } catch (_) {
          // Keep default min-height
        }
      });
    }
  }

  function switchPage(pageKey, opts = {}) {
    const pages = {
      today: $('#v4PageToday'),
      newsletter: $('#v4PageNewsletter'),
      analysis: $('#v4PageAnalysis'),
      b2b: $('#v4PageB2B')
    };
    if (!pages[pageKey]) pageKey = 'today';
    state.activePage = pageKey;

    Object.entries(pages).forEach(([k, el]) => {
      if (el) el.hidden = k !== pageKey;
    });

    $$('[data-drawer-page]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.drawerPage === pageKey);
    });
    $$('[data-switch-page]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.switchPage === pageKey);
    });

    const communityCta = $('#v4CommunityCta');
    if (communityCta) {
      communityCta.hidden = pageKey === 'newsletter';
    }

    if (opts.syncHash !== false && window.location.protocol !== 'file:' && window.history && window.history.replaceState) {
      const cleanBase = getCleanPortalPath() + window.location.search;
      window.history.replaceState(null, '', pageKey === 'today' ? cleanBase : `${cleanBase}#${pageKey}`);
    }

    if (pageKey === 'newsletter') {
      loadNewsletterPreview();
    }
    applyFilters();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  // ─── CHẾ ĐỘ LỌC CHUYÊN MỤC & TÌM KIẾM ────────────────────────────────────
  function applyFilters() {
    const isToday = state.activePage === 'today';
    const tabs = $$('#v4CatTabs .v4-cat-btn');
    tabs.forEach((btn) => {
      const active = isToday && btn.dataset.cat === state.activeCategory;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', String(active));
    });

    $$('[data-drawer-cat]').forEach((btn) => {
      btn.classList.toggle('active', isToday && btn.dataset.drawerCat === state.activeCategory);
    });

    const frontView = $('#v4FrontPageView');
    const filteredView = $('#v4FilteredView');
    const clearBtn = $('#v4SearchClear');
    const needle = state.searchTerm.trim().toLowerCase();

    if (clearBtn) clearBtn.hidden = !needle;

    const homeBtn = $('#v4HomeIconBtn');
    if (homeBtn) {
      homeBtn.classList.toggle('active', isToday && state.activeCategory === 'ALL' && !needle);
    }

    if (!isToday) return;

    if (state.activeCategory === 'ALL' && !needle) {
      if (frontView) frontView.hidden = false;
      if (filteredView) filteredView.hidden = true;
      return;
    }

    if (frontView) frontView.hidden = true;
    if (filteredView) filteredView.hidden = false;

    const allNews = state.data.eligibleNewsList || [];
    const matches = allNews
      .filter((item) => {
        const matchCat = state.activeCategory === 'ALL' || item.category === state.activeCategory;
        const matchQ =
          !needle ||
          String(item.headline || '').toLowerCase().includes(needle) ||
          String(item.summary || '').toLowerCase().includes(needle) ||
          String(item.publisher || '').toLowerCase().includes(needle) ||
          String(item.category || '').toLowerCase().includes(needle);
        return matchCat && matchQ;
      })
      .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''));

    const matchedIds = new Set(matches.map((m) => m.eventId));
    const otherNews = allNews
      .filter((it) => !matchedIds.has(it.eventId))
      .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''))
      .slice(0, 5);

    const catCounts = {};
    allNews.forEach((it) => {
      if (it.category) catCounts[it.category] = (catCounts[it.category] || 0) + 1;
    });

    const headingText =
      state.activeCategory === 'ALL'
        ? `Kết quả tìm kiếm: "${state.searchTerm.trim()}"`
        : `${catLabel(state.activeCategory)}${needle ? ` · lọc "${state.searchTerm.trim()}"` : ''}`;

    const rowsHtml = matches.length
      ? `<div class="v4-filtered-list">
          ${matches
            .map(
              (it) => `
            <article class="v4-filtered-row">
              <div class="v4-thumb-wrap" data-open-event="${esc(it.eventId)}" style="cursor:pointer;">${imgTag(it.imageUrl, it.headline, 'v4-thumb-img')}</div>
              <div>
                <div class="v4-crimson-tag" style="margin-bottom:4px;">${esc(catLabel(it.category))}</div>
                <h3 class="v4-filtered-row-title" data-open-event="${esc(it.eventId)}">${esc(it.headline || it.title)}</h3>
                <p class="v4-filtered-row-sapo">${esc(it.summary || '')}</p>
                <div class="v4-filtered-row-actions">
                  <div class="v4-article-meta">
                    <span>${esc(sourceLabel(it))}</span>
                    <span aria-hidden="true">·</span>
                    <span class="v4-mono-time">${esc(extractDateTimeReadable(it))}</span>
                  </div>
                  <button type="button" class="v4-filtered-read-btn" data-open-event="${esc(it.eventId)}">Đọc phân tích chi tiết &rarr;</button>
                  ${
                    it.sourceUrl
                      ? `<a href="${esc(it.sourceUrl)}" target="_blank" rel="noopener noreferrer" class="v4-filtered-orig-link">Nguồn báo gốc &nearr;</a>`
                      : ''
                  }
                </div>
              </div>
            </article>
          `
            )
            .join('')}
        </div>`
      : `<p class="v4-sec-subtitle">Không có bản tin nào khớp bộ lọc hiện tại.</p>`;

    const otherNewsBlockHtml = otherNews.length
      ? `<div class="v4-sidebar-block">
          <div class="v4-col-label">
            <span>Tin khác trong phiên</span>
            <span class="v4-col-label-sub">Đọc thêm</span>
          </div>
          <div class="v4-feed-list">
            ${otherNews
              .map(
                (it) => `
              <article class="v4-feed-item" data-open-event="${esc(it.eventId)}">
                <div class="v4-feed-meta">
                  <span class="v4-crimson-tag">${esc(catLabel(it.category))}</span>
                  <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                </div>
                <h3 class="v4-feed-title">${esc(it.headline || it.title)}</h3>
              </article>
            `
              )
              .join('')}
          </div>
        </div>`
      : '';

    const catSidebarHtml = `
      <div class="v4-sidebar-block">
        <div class="v4-col-label">
          <span>Chuyên mục phiên</span>
          <span class="v4-col-label-sub">${allNews.length} tin</span>
        </div>
        <div class="v4-sidebar-cats">
          <button type="button" class="v4-sidebar-cat-btn ${state.activeCategory === 'ALL' ? 'active' : ''}" data-filter-cat="ALL">
            <span>Trang nhất (Tất cả)</span>
            <span class="v4-sidebar-cat-count">${allNews.length}</span>
          </button>
          ${CATEGORIES.map((c) => {
            const cnt = catCounts[c.key] || 0;
            const active = state.activeCategory === c.key ? 'active' : '';
            return `
              <button type="button" class="v4-sidebar-cat-btn ${active}" data-filter-cat="${esc(c.key)}">
                <span>${esc(c.label)}</span>
                <span class="v4-sidebar-cat-count">${cnt}</span>
              </button>
            `;
          }).join('')}
        </div>
      </div>
    `;

    filteredView.innerHTML = `
      <div class="v4-filtered-head">
        <div>
          <h2 class="v4-sec-title">${esc(headingText)}</h2>
          <p class="v4-sec-subtitle" style="margin-top:6px; padding-left:12px;">Tìm thấy ${matches.length} bản tin phù hợp trong ấn bản</p>
        </div>
        <button type="button" class="v4-back-front-btn" id="v4BackFrontBtn">&larr; Quay lại Trang nhất</button>
      </div>

      <div class="v4-filtered-layout">
        <div class="v4-filtered-main">${rowsHtml}</div>
        <aside class="v4-filtered-sidebar" aria-label="Tin khác và danh mục trong phiên">
          ${otherNewsBlockHtml}
          ${catSidebarHtml}
        </aside>
      </div>
    `;

    const backBtn = $('#v4BackFrontBtn');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        state.activeCategory = 'ALL';
        state.searchTerm = '';
        const input = $('#v4SearchInput');
        if (input) input.value = '';
        applyFilters();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  // ─── ACCESSIBLE FOCUS TRAP & DRAWER READER ─────────────────────────────────
  const OVERLAY_SELECTORS = '#v4Drawer, #v4NavDrawer, #v4VCardModal, #v4WelcomeModal';
  const LANDMARK_SELECTORS =
    '.v4-skip-link, #v4Header, .v4-cat-nav, #v4PulseStrip, #mainContent, #v4CommunityCta, #siteFooter, #v4FloatWidget';
  let activeTrap = null;
  let lastExternalFocus = null;

  function setBackgroundInert(isInert, activeEl) {
    $$(LANDMARK_SELECTORS).forEach((el) => {
      if (activeEl && el.contains(activeEl)) return;
      if (isInert) {
        el.setAttribute('aria-hidden', 'true');
        el.inert = true;
      } else {
        el.removeAttribute('aria-hidden');
        el.inert = false;
      }
    });
  }

  function isElementVisible(el) {
    if (!el || el.disabled || el.closest('[hidden]') || el.closest('[aria-hidden="true"]')) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    return el.getClientRects().length > 0;
  }

  function getFocusable(container) {
    if (!container) return [];
    return Array.from(
      container.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    ).filter(isElementVisible);
  }

  function activateTrap(overlayEl, onClose) {
    if (!overlayEl) return;
    const currentFocus = document.activeElement;
    if (
      currentFocus &&
      currentFocus !== document.body &&
      currentFocus !== document.documentElement &&
      !currentFocus.closest(OVERLAY_SELECTORS)
    ) {
      lastExternalFocus = currentFocus;
    } else if (!lastExternalFocus || !document.contains(lastExternalFocus)) {
      lastExternalFocus = null;
    }

    const prevTrigger =
      currentFocus && currentFocus !== document.body && !currentFocus.closest(OVERLAY_SELECTORS)
        ? currentFocus
        : lastExternalFocus;

    if (activeTrap) {
      if (activeTrap.handler) document.removeEventListener('keydown', activeTrap.handler, true);
      if (activeTrap.focusHandler) document.removeEventListener('focusin', activeTrap.focusHandler, true);
    }

    // Move focus out of background landmarks BEFORE setting aria-hidden / inert
    if (!overlayEl.hasAttribute('tabindex')) overlayEl.setAttribute('tabindex', '-1');
    const syncItems = getFocusable(overlayEl);
    if (syncItems.length) {
      syncItems[0].focus({ preventScroll: true });
    } else {
      overlayEl.focus({ preventScroll: true });
    }
    setBackgroundInert(true, overlayEl);

    const handler = (e) => {
      if (!activeTrap || activeTrap.overlayEl !== overlayEl) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key === 'Tab') {
        const items = getFocusable(overlayEl);
        if (!items.length) {
          e.preventDefault();
          return;
        }
        const first = items[0];
        const last = items[items.length - 1];
        if (first === last) {
          e.preventDefault();
          first.focus({ preventScroll: true });
          return;
        }
        if (e.shiftKey) {
          if (document.activeElement === first || !overlayEl.contains(document.activeElement)) {
            e.preventDefault();
            last.focus({ preventScroll: true });
          }
        } else if (document.activeElement === last || !overlayEl.contains(document.activeElement)) {
          e.preventDefault();
          first.focus({ preventScroll: true });
        }
      }
    };

    const focusHandler = (e) => {
      if (!activeTrap || activeTrap.overlayEl !== overlayEl || overlayEl.hidden) return;
      if (!overlayEl.contains(e.target)) {
        e.stopPropagation();
        const items = getFocusable(overlayEl);
        const fallback = items[0] || overlayEl;
        if (fallback === overlayEl && !overlayEl.hasAttribute('tabindex')) {
          overlayEl.setAttribute('tabindex', '-1');
        }
        fallback.focus({ preventScroll: true });
      }
    };

    document.addEventListener('keydown', handler, true);
    document.addEventListener('focusin', focusHandler, true);
    activeTrap = { overlayEl, prevTrigger, handler, focusHandler };

    setTimeout(() => {
      if (overlayEl.hidden) return;
      if (overlayEl.contains(document.activeElement) && document.activeElement !== overlayEl) return;
      const items = getFocusable(overlayEl);
      if (items.length) {
        items[0].focus({ preventScroll: true });
      }
    }, 30);
  }

  function deactivateTrap(overlayEl, restoreFocus = true) {
    const anyOpen = [$( '#v4Drawer' ), $( '#v4NavDrawer' ), $( '#v4VCardModal' ), $( '#v4WelcomeModal' )].some(
      (el) => el && !el.hidden
    );
    if (!anyOpen) {
      setBackgroundInert(false);
      document.body.style.overflow = '';
    }
    if (activeTrap && (!overlayEl || activeTrap.overlayEl === overlayEl)) {
      const { prevTrigger, handler, focusHandler } = activeTrap;
      if (handler) document.removeEventListener('keydown', handler, true);
      if (focusHandler) document.removeEventListener('focusin', focusHandler, true);
      activeTrap = null;
      if (restoreFocus && !anyOpen) {
        const targetRestore =
          (prevTrigger && document.contains(prevTrigger) && isElementVisible(prevTrigger) ? prevTrigger : null) ||
          (lastExternalFocus && document.contains(lastExternalFocus) && isElementVisible(lastExternalFocus)
            ? lastExternalFocus
            : null);
        if (targetRestore) {
          targetRestore.focus({ preventScroll: true });
        }
        lastExternalFocus = null;
      }
    }
  }

  function openDrawer(kicker, bodyHtml) {
    const drawer = $('#v4Drawer');
    $('#v4DrawerKicker').textContent = kicker;
    $('#v4DrawerBody').innerHTML = bodyHtml;
    $('#v4DrawerBackdrop').hidden = false;
    drawer.hidden = false;
    document.body.style.overflow = 'hidden';
    activateTrap(drawer, closeDrawer);
  }

  function closeDrawer(restoreFocus = true) {
    const drawer = $('#v4Drawer');
    $('#v4DrawerBackdrop').hidden = true;
    drawer.hidden = true;
    deactivateTrap(drawer, restoreFocus);
  }

  function openArticleDrawer(eventId) {
    const item = state.newsById[eventId];
    if (!item) return;

    const blocks = [
      { label: '01 · Bối cảnh & Động thái chính', text: item.briefingContext || item.sectionB_context },
      { label: '02 · Dữ kiện & Con số trọng tâm', text: item.briefingFacts || item.sectionA_whatHappened },
      { label: '03 · Tác động thị trường', text: item.briefingPerspective || item.sectionC_whyItMatters },
      { label: '04 · Hệ lụy & Góc nhìn doanh nghiệp', text: item.briefingImplication || item.sectionD_macroMicro },
      { label: '05 · Liên hệ hạ tầng Fintech & Thanh toán', text: item.fintechRelevance || item.sectionE_fintechLens },
      { label: '06 · Khuyến nghị hành động', text: item.sectionG_practicalTakeaway }
    ].filter((b) => b.text && String(b.text).trim().length > 0);

    const html = `
      <span class="v4-crimson-tag">${esc(catLabel(item.category))}</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(item.headline || item.title)}</h2>
      <div class="v4-drawer-meta">
        <span>Nguồn: <strong>${esc(sourceLabel(item))}</strong></span>
        <span aria-hidden="true"> · </span>
        <span class="v4-mono-time">${esc(extractDateTimeReadable(item))}</span>
      </div>
      ${item.imageUrl ? imgTag(item.imageUrl, item.headline, 'v4-drawer-img') : ''}
      ${item.supportingQuote ? `<blockquote class="v4-drawer-quote">“${esc(item.supportingQuote)}”</blockquote>` : ''}
      ${blocks
        .map(
          (b) => `
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">${esc(b.label)}</div>
          <p class="v4-drawer-block-text">${esc(b.text)}</p>
        </div>
      `
        )
        .join('')}
      <div class="v4-drawer-actions">
        ${
          item.sourceUrl
            ? `<a href="${esc(item.sourceUrl)}" target="_blank" rel="noopener noreferrer" class="v4-btn-navy">Đọc bài gốc (${esc(sourceLabel(item))}) &nearr;</a>`
            : ''
        }
      </div>
    `;
    openDrawer(`${item.eventId} · Tóm tắt phân tích`, html);
  }

  function openMarketPulseDrawer(m) {
    if (!m) return;
    const isNotVerified = m.verificationStatus === '72H_NOT_VERIFIED';
    const primaryArticleUrl = m.dailyArticleUrl || m.sourceUrl;
    const secUrls = (m.secondarySourceUrls || []).filter(
      (u) => u && /^https?:\/\//i.test(u) && u !== m.sourceUrl && u !== m.dailyArticleUrl
    );

    const html = `
      <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px;">
        <span class="v4-crimson-tag">THẺ ${esc(m.cardNumber || '')} · ${esc(m.tierGroup || 'MARKET PULSE')}</span>
        <span class="v4-readiness-pill ${isNotVerified ? 'is-idea' : 'is-confirmed'}">${esc(m.verificationStatus || 'VERIFIED')}</span>
      </div>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(m.label || m.shortLabel)}</h2>
      <div class="v4-drawer-meta">
        <span>Giá trị hiện tại: <strong class="v4-mono-time">${esc(m.value)}</strong></span>
        <span aria-hidden="true"> · </span>
        <span>Biến động: <strong>${esc(m.compactDelta || m.change || '--')}</strong></span>
      </div>
      ${
        isNotVerified
          ? `<div class="v4-drawer-alert is-warning">
              <strong>Thông báo kiểm định Freshness 72h:</strong> Số liệu kỳ quan sát chưa có công bố chính thức kèm timestamp đối soát trong vòng 72 giờ qua. Giá trị tham khảo gần nhất: <strong>${esc(m.referenceValue || 'Kỳ quan sát trước')}</strong>.
            </div>`
          : ''
      }
      ${
        m.key === 'vietqrVolume'
          ? `<div class="v4-drawer-alert">
              <strong>Lưu ý phạm vi dữ liệu:</strong> Mức tăng trưởng <strong>${esc(m.value)}</strong> áp dụng riêng cho luồng khách du lịch quốc tế và điểm bán chấp nhận <strong>VietQR Global (Inbound &amp; Cross-border)</strong>, không đồng nhất với tổng sản lượng toàn hệ thống NAPAS.
            </div>`
          : ''
      }
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Thông tin quan sát &amp; Chu kỳ</div>
        <div class="v4-drawer-meta-grid">
          <div><strong>Tên chỉ số:</strong> ${esc(m.label || m.shortLabel)}</div>
          <div><strong>Mã tham chiếu:</strong> <span class="v4-mono-time">${esc(m.referenceCode || m.key || '')}</span></div>
          <div><strong>Ngày quan sát:</strong> ${esc(m.observationAt || m.asOf || '--')}</div>
          <div><strong>Ngày công bố:</strong> ${esc(m.publishedAt || m.asOf || '--')}</div>
          ${m.dataPeriod ? `<div class="v4-drawer-meta-span"><strong>Kỳ dữ liệu:</strong> ${esc(m.dataPeriod)}</div>` : ''}
          ${m.referenceValue ? `<div class="v4-drawer-meta-span"><strong>Thông số tham chiếu gốc:</strong> ${esc(m.referenceValue)}</div>` : ''}
        </div>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Nguồn gốc &amp; Đường dẫn xác minh</div>
        <p class="v4-drawer-block-text">
          <strong>Cơ quan / Nguồn công bố:</strong> ${esc(m.sourceName || m.sourceShortName || 'Báo chí chính thống')}<br>
          ${m.searchKeyword || m.referenceCode ? `<strong>Từ khóa quét cố định:</strong> <span class="v4-mono-time">${esc(m.referenceCode || m.searchKeyword)}</span><br>` : ''}
          ${m.articleTitle ? `<strong>Bài báo đối soát:</strong> ${esc(m.articleTitle)}` : ''}
        </p>
        <div class="v4-drawer-links-row">
          ${
            primaryArticleUrl
              ? `<a href="${esc(primaryArticleUrl)}" target="_blank" rel="noopener noreferrer" class="v4-btn-navy">Mở bài báo đối soát (${esc(m.sourceShortName || 'Bài báo')}) &nearr;</a>`
              : ''
          }
          ${
            m.sourceUrl && m.sourceUrl !== primaryArticleUrl
              ? `<a href="${esc(m.sourceUrl)}" target="_blank" rel="noopener noreferrer" class="v4-vcard-action-btn">Kênh tra cứu gốc &nearr;</a>`
              : ''
          }
          ${secUrls
            .map(
              (u, idx) =>
                `<a href="${esc(u)}" target="_blank" rel="noopener noreferrer" class="v4-vcard-action-btn">Nguồn bổ trợ #${idx + 1} &nearr;</a>`
            )
            .join('')}
        </div>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Diễn giải tài chính &amp; Tác động thực tế</div>
        <p class="v4-drawer-block-text">${esc(m.financialInterpretation || m.implication || m.statusReason || m.note || '')}</p>
      </div>
      ${
        m.monitoringWatchpoint
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">Điểm cần theo dõi tiếp theo</div>
              <p class="v4-drawer-block-text">${esc(m.monitoringWatchpoint)}</p>
            </div>`
          : ''
      }
    `;
    openDrawer('Market Pulse · Đối soát chi tiết', html);
  }

  function openDecisionSignalDrawer(signalId) {
    const signals = state.data?.editorialSections?.sec04b_decisionBrief?.signals || [];
    const sig = signals.find((s, idx) => (s.signalId || `DECISION-0${idx + 1}`) === signalId);
    if (!sig) return;

    const assumptionsText = Array.isArray(sig.assumptions)
      ? sig.assumptions.join('; ')
      : typeof sig.assumptions === 'string'
        ? sig.assumptions
        : '';
    const risksText = Array.isArray(sig.risks)
      ? sig.risks.join('; ')
      : typeof sig.risks === 'string'
        ? sig.risks
        : '';
    const segmentsText = Array.isArray(sig.relevantMerchantSegments)
      ? sig.relevantMerchantSegments.join(', ')
      : sig.relevantMerchantSegments || 'Chuỗi F&B, Khách sạn, Bán lẻ đa kênh & Hộ kinh doanh';

    const solutionsHtml = (sig.potentialPaymentSolutions || [])
      .map((sol) => {
        let cls = 'is-confirmed';
        let label = 'ĐÃ CÓ SẴN TẠI PAYOO (HIỆN HỮU)';
        if (sol.readinessType === 'POTENTIAL_INTEGRATION') {
          cls = 'is-potential';
          label = 'CẦN TÍCH HỢP MỞ RỘNG';
        } else if (sol.readinessType === 'PRODUCT_DEVELOPMENT_IDEA') {
          cls = 'is-idea';
          label = 'Ý TƯỞNG PHÁT TRIỂN MỚI';
        }
        return `
          <div class="v4-readiness-item">
            <span class="v4-readiness-pill ${cls}">${esc(label)}</span>
            <div style="font-weight:700; font-size:14.5px; color:var(--v4-text); margin-bottom:4px;">${esc(sol.solutionName || '')}</div>
            <p class="v4-drawer-block-text">${esc(sol.capabilityNote || '')}</p>
          </div>
        `;
      })
      .join('');

    let urls = Array.isArray(sig.evidenceUrls) ? sig.evidenceUrls.slice() : [];
    if (!urls.length && Array.isArray(sig.relatedEventIds) && sig.relatedEventIds.length) {
      urls = sig.relatedEventIds
        .map((eid) => {
          const found = state.newsById[eid];
          return found ? found.canonicalUrl || found.sourceUrl : null;
        })
        .filter(Boolean);
    }
    urls = urls.filter((u) => /^https?:\/\//i.test(u));

    const confLabel =
      !sig.confidenceLevel || String(sig.confidenceLevel).includes('HIGH')
        ? 'ĐỘ TIN CẬY CAO · ĐÃ XÁC MINH'
        : 'TRỌNG TÂM ĐIỀU HÀNH';

    const html = `
      <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px;">
        <span class="v4-crimson-tag">${esc(sig.categoryBadge || 'TÍN HIỆU CHIẾN LƯỢC')}</span>
        <span class="v4-b2b-pill">${esc(confLabel)}</span>
      </div>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(sig.signalTitle || '')}</h2>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">A · Sự kiện nào đã xảy ra?</div>
        <p class="v4-drawer-block-text">${esc(sig.whatHappened || '')}</p>
      </div>
      ${
        sig.whyItMatters
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">B · Vì sao đáng chú ý?</div>
              <p class="v4-drawer-block-text">${esc(sig.whyItMatters)}</p>
            </div>`
          : ''
      }
      ${
        sig.whatChanges
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">C · Tác động nào có thể xảy ra?</div>
              <p class="v4-drawer-block-text">${esc(sig.whatChanges)}</p>
            </div>`
          : ''
      }
      ${
        sig.whatItMeansForMyWork
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">D · Liên quan gì đến thanh toán &amp; công việc B2B?</div>
              <p class="v4-drawer-block-text"><strong>${esc(sig.whatItMeansForMyWork)}</strong></p>
            </div>`
          : ''
      }
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">E · Cơ hội, Phân khúc, Giả định &amp; Rủi ro</div>
        <p class="v4-drawer-block-text">
          <strong>Phân khúc khách hàng:</strong> ${esc(segmentsText)}
          ${assumptionsText ? `<br><strong>Giả định:</strong> ${esc(assumptionsText)}` : ''}
          ${risksText ? `<br><strong>Rủi ro cần lường trước:</strong> ${esc(risksText)}` : ''}
        </p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">F · Tôi nên làm gì hoặc theo dõi gì?</div>
        ${sig.whatShouldIDoOrWatch ? `<p class="v4-drawer-block-text" style="margin-bottom:8px;">${esc(sig.whatShouldIDoOrWatch)}</p>` : ''}
        <p class="v4-drawer-block-text">
          <strong>Hành động tiếp theo đề xuất:</strong> ${esc(sig.proposedNextAction || '')}
          ${sig.monitoringTimeHorizon ? `<br><strong>Khung thời gian theo dõi:</strong> ${esc(sig.monitoringTimeHorizon)}` : ''}
        </p>
      </div>
      ${
        solutionsHtml
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">G · Sản phẩm &amp; Giải pháp Payoo liên quan</div>
              ${solutionsHtml}
            </div>`
          : ''
      }
      ${
        urls.length
          ? `<div class="v4-drawer-block">
              <div class="v4-drawer-block-label">H · Nguồn báo chí tham khảo &amp; Đối soát (${urls.length})</div>
              <div class="v4-drawer-links-row">
                ${urls
                  .map(
                    (u, idx) =>
                      `<a href="${esc(u)}" target="_blank" rel="noopener noreferrer" class="v4-vcard-action-btn">Nguồn đối soát #${idx + 1} &nearr;</a>`
                  )
                  .join('')}
              </div>
            </div>`
          : ''
      }
    `;
    openDrawer(`${sig.signalId || signalId} · Phân tích điều hành B2B`, html);
  }

  function openFintechItemDrawer(item) {
    if (!item) return;
    if (item.kind === 'framework') {
      const fw = item.payload;
      const html = `
        <span class="v4-crimson-tag">${esc(item.kicker)}</span>
        <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(fw.frameworkTitle)}</h2>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 01 · Tác động vĩ mô</div>
          <p class="v4-drawer-block-text">${esc(fw.step1 || '')}</p>
        </div>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 02 · Năng lực ngân hàng số</div>
          <p class="v4-drawer-block-text">${esc(fw.step2 || '')}</p>
        </div>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 03 · Điểm chạm thanh toán bán lẻ</div>
          <p class="v4-drawer-block-text">${esc(fw.step3 || '')}</p>
        </div>
      `;
      openDrawer('Góc chuyên môn Fintech', html);
      return;
    }

    const l = item.payload;
    const html = `
      <span class="v4-crimson-tag">${esc(l.concept || 'Chuyên đề Fintech')}</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(l.title || l.topic)}</h2>
      <div class="v4-drawer-meta">${esc(l.newsGrounding || '')}</div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Giải thích cơ chế</div>
        <p class="v4-drawer-block-text">${esc(l.simpleExplanation || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Ví dụ thực tiễn</div>
        <p class="v4-drawer-block-text">${esc(l.realWorldExample || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Tác động đối với doanh nghiệp</div>
        <p class="v4-drawer-block-text">${esc(l.impactOnBusiness || l.takeaway || '')}</p>
      </div>
    `;
    openDrawer('Góc chuyên môn Fintech', html);
  }

  function openPlaybookDrawer(pb) {
    if (!pb) return;
    const html = `
      <span class="v4-crimson-tag">PLAYBOOK TRIỂN KHAI B2B</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(pb.title)}</h2>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Nhóm khách hàng mục tiêu</div>
        <p class="v4-drawer-block-text">${esc(pb.target || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Đề xuất giá trị cốt lõi (Pitch)</div>
        <p class="v4-drawer-block-text">${esc(pb.pitch || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Xử lý rào cản &amp; Từ chối</div>
        <p class="v4-drawer-block-text">${esc(pb.objectionHandling || '')}</p>
      </div>
    `;
    openDrawer('Playbook B2B · Triển khai thực tế', html);
  }

  // ─── LEFT DRAWER, THEME, VCARD QR MODAL & WELCOME MODAL ─────────────────────
  function openNavDrawer() {
    const drawer = $('#v4NavDrawer');
    $('#v4NavBackdrop').hidden = false;
    drawer.hidden = false;
    $('#v4MenuBtn')?.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    activateTrap(drawer, closeNavDrawer);
  }

  function closeNavDrawer(restoreFocus = true) {
    const drawer = $('#v4NavDrawer');
    $('#v4NavBackdrop').hidden = true;
    drawer.hidden = true;
    $('#v4MenuBtn')?.setAttribute('aria-expanded', 'false');
    deactivateTrap(drawer, restoreFocus);
  }

  function switchVCardTab(type) {
    state.vcardTab = QR_SVG_DATA[type] ? type : 'vcard';
    $$('[data-vcard-tab]').forEach((btn) => {
      const active = btn.dataset.vcardTab === state.vcardTab;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', String(active));
    });
    const qrData = QR_SVG_DATA[state.vcardTab];
    const container = $('#v4VCardQrContainer');
    if (container) {
      container.innerHTML = `<svg viewBox="0 0 ${qrData.size} ${qrData.size}" shape-rendering="crispEdges" role="img" aria-label="Mã QR ${esc(state.vcardTab)}"><rect width="${qrData.size}" height="${qrData.size}" fill="#ffffff"/><path d="${qrData.path}" fill="${qrData.color}"/></svg>`;
    }
    const hint = $('#v4VCardScanHint');
    if (hint) {
      if (state.vcardTab === 'zalo') {
        hint.textContent = 'Quét bằng Camera hoặc Zalo để nhắn tin trực tiếp với Quang Trí (Bryan)';
      } else if (state.vcardTab === 'linkedin') {
        hint.textContent = 'Quét để mở hồ sơ LinkedIn chính thức của Bryan Nguyen';
      } else {
        hint.textContent = 'Đưa Camera iPhone vào quét để lưu thẳng Danh bạ trong 1 giây';
      }
    }
  }

  function openVCardModal() {
    const modal = $('#v4VCardModal');
    switchVCardTab(state.vcardTab);
    $('#v4VCardBackdrop').hidden = false;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    activateTrap(modal, closeVCardModal);
  }

  function closeVCardModal(restoreFocus = true) {
    const modal = $('#v4VCardModal');
    $('#v4VCardBackdrop').hidden = true;
    modal.hidden = true;
    deactivateTrap(modal, restoreFocus);
  }

  function downloadVCard() {
    const vcfContent = [
      'BEGIN:VCARD',
      'VERSION:3.0',
      'N:Nguyen;Bryan (Huynh Quang Tri);;;',
      'FN:Bryan Nguyen (Nguyen Huynh Quang Tri)',
      'ORG:Payoo (VietUnion)',
      'TITLE:Enterprise B2B & Fintech Executive',
      'TEL;TYPE=CELL,VOICE:+84838673639',
      'EMAIL;TYPE=WORK,INTERNET:quangtritc1805@gmail.com',
      'URL:https://bryanportfolio.io.vn/',
      'ITEM1.URL:https://www.linkedin.com/in/bryan-nguyen-796a7b1ab/',
      'ITEM1.X-ABLabel:LinkedIn',
      'ITEM2.URL:https://zalo.me/0838673639',
      'ITEM2.X-ABLabel:Zalo',
      'ADR;TYPE=WORK:;;Ho Chi Minh City;;;Vietnam',
      'NOTE:Enterprise B2B Development & FinTech Infrastructure | Master of Business Analytics (UOW)',
      'END:VCARD'
    ].join('\r\n');

    const blob = new Blob([vcfContent], { type: 'text/vcard;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Bryan_Nguyen_Payoo_vCard.vcf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function copyVCardLink(btn) {
    const url = 'https://bryanportfolio.io.vn/';
    const done = () => {
      if (!btn) return;
      if (!btn.dataset.origLabel) btn.dataset.origLabel = btn.textContent;
      btn.textContent = 'Đã sao chép ✓';
      clearTimeout(btn._copyTimer);
      btn._copyTimer = setTimeout(() => {
        btn.textContent = btn.dataset.origLabel;
      }, 2000);
    };
    const fallbackCopy = () => {
      const ta = document.createElement('textarea');
      ta.value = url;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        done();
      } catch (_) {}
      document.body.removeChild(ta);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done).catch(fallbackCopy);
    } else {
      fallbackCopy();
    }
  }

  function openWelcomeModal() {
    const modal = $('#v4WelcomeModal');
    if (!modal) return;
    $('#v4WelcomeBackdrop').hidden = false;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    activateTrap(modal, () => closeWelcomeModal(true));
  }

  function closeWelcomeModal(persist = true, restoreFocus = true) {
    const modal = $('#v4WelcomeModal');
    if (!modal) return;
    $('#v4WelcomeBackdrop').hidden = true;
    modal.hidden = true;
    if (persist) {
      try {
        localStorage.setItem(WELCOME_STORAGE_KEY, 'true');
      } catch (_) {}
    }
    deactivateTrap(modal, restoreFocus);
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    const logoPath = isDark ? `${ROOT_ASSET_BASE}bnews-logo-dark.svg` : `${ROOT_ASSET_BASE}bnews-logo-light.svg`;
    $$('.v4-brand-logo, .v4-nav-drawer-logo, .v4-footer-logo').forEach((img) => {
      img.src = logoPath;
    });
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) {
      themeMeta.setAttribute('content', isDark ? '#0B0F19' : '#0A3D7A');
    }
    const tBtn = $('#v4ThemeToggleBtn');
    if (tBtn) {
      tBtn.textContent = isDark ? 'Chuyển sang Giao diện Sáng' : 'Đổi giao diện Sáng / Tối';
    }
  }

  function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    localStorage.setItem('site_theme', next);
    localStorage.removeItem('ms-theme');
    applyTheme(next);
  }

  // ─── EVENTS & INITIALIZATION ──────────────────────────────────────────────
  function bindNewsletterForm(formSel, inputSel, feedbackSel, sourceLabel) {
    const form = $(formSel);
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = $(inputSel);
      const fb = $(feedbackSel);
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!input || !fb) return;

      const email = (input.value || '').trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        fb.hidden = false;
        fb.classList.add('is-error');
        fb.textContent = 'Vui lòng nhập địa chỉ email hợp lệ (ví dụ: tenban@gmail.com).';
        input.focus();
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.origText = submitBtn.textContent;
        submitBtn.textContent = 'Đang đăng ký...';
      }

      try {
        const saved = JSON.parse(localStorage.getItem('bnews_subscribers') || '[]');
        if (Array.isArray(saved) && !saved.includes(email)) {
          saved.push(email);
          localStorage.setItem('bnews_subscribers', JSON.stringify(saved));
        }
      } catch (_) {}

      fetch(BNEWS_SUBSCRIBE_WEBHOOK_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          source: sourceLabel,
          timestamp: new Date().toISOString()
        })
      })
        .catch(() => {})
        .finally(() => {
          fb.hidden = false;
          fb.classList.remove('is-error');
          fb.textContent = `Đăng ký thành công! Bản tin Bnews sáng mai sẽ gửi tới ${email} lúc 9h00.`;
          input.value = '';
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.origText || 'Đăng ký nhận bản tin →';
          }
        });
    });
  }

  function resetToFrontPage(e) {
    if (e) e.preventDefault();
    state.activeCategory = 'ALL';
    state.searchTerm = '';
    const input = $('#v4SearchInput');
    if (input) input.value = '';
    switchPage('today');
  }

  function updateBackToTopState() {
    const btn = $('#v4BackToTopBtn');
    if (btn) btn.classList.toggle('is-visible', window.scrollY > 350);
  }

  function bindGlobalEvents() {
    document.addEventListener('click', (e) => {
      const eventTrigger = e.target.closest('[data-open-event]');
      if (eventTrigger) {
        e.preventDefault();
        openArticleDrawer(eventTrigger.dataset.openEvent);
        return;
      }

      const signalTrigger = e.target.closest('[data-open-signal]');
      if (signalTrigger) {
        e.preventDefault();
        openDecisionSignalDrawer(signalTrigger.dataset.openSignal);
        return;
      }

      const pageBtn = e.target.closest('[data-switch-page], [data-drawer-page]');
      if (pageBtn) {
        const targetPage = pageBtn.dataset.switchPage || pageBtn.dataset.drawerPage;
        closeNavDrawer(false);
        switchPage(targetPage);
        return;
      }

      const drawerCatBtn = e.target.closest('[data-drawer-cat]');
      if (drawerCatBtn) {
        state.activeCategory = drawerCatBtn.dataset.drawerCat;
        closeNavDrawer(false);
        switchPage('today');
        return;
      }

      const catFilterTrigger = e.target.closest('[data-filter-cat]');
      if (catFilterTrigger) {
        state.activeCategory = catFilterTrigger.dataset.filterCat;
        if (state.activeCategory === 'ALL') {
          state.searchTerm = '';
          const input = $('#v4SearchInput');
          if (input) input.value = '';
        }
        switchPage('today');
        return;
      }

      const fw = $('#v4FloatWidget');
      if (fw && fw.classList.contains('is-open') && !e.target.closest('#v4FloatWidget')) {
        fw.classList.remove('is-open');
        $('#v4FabToggleBtn')?.setAttribute('aria-expanded', 'false');
      }
    });

    $$('#v4CatTabs .v4-cat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeCategory = btn.dataset.cat;
        switchPage('today');
      });
    });

    // WAI-ARIA Arrow key support on Category Tablist & Macro Step Bar
    $('#v4CatTabs')?.addEventListener('keydown', (e) => {
      const tabs = $$('#v4CatTabs .v4-cat-btn');
      const idx = tabs.indexOf(document.activeElement);
      if (idx === -1) return;
      let nextIdx = -1;
      if (e.key === 'ArrowRight') nextIdx = (idx + 1) % tabs.length;
      else if (e.key === 'ArrowLeft') nextIdx = (idx - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') nextIdx = 0;
      else if (e.key === 'End') nextIdx = tabs.length - 1;
      if (nextIdx !== -1) {
        e.preventDefault();
        tabs[nextIdx].focus();
        state.activeCategory = tabs[nextIdx].dataset.cat;
        switchPage('today');
      }
    });

    $('#v4StepBar')?.addEventListener('keydown', (e) => {
      const steps = $$('#v4StepBar .v4-step-btn');
      const idx = steps.indexOf(document.activeElement);
      if (idx === -1) return;
      let nextIdx = -1;
      if (e.key === 'ArrowRight') nextIdx = (idx + 1) % steps.length;
      else if (e.key === 'ArrowLeft') nextIdx = (idx - 1 + steps.length) % steps.length;
      else if (e.key === 'Home') nextIdx = 0;
      else if (e.key === 'End') nextIdx = steps.length - 1;
      if (nextIdx !== -1) {
        e.preventDefault();
        state.activeLayerIdx = Number(steps[nextIdx].dataset.layerIdx);
        renderMacroMicro();
        $('#v4StepBar .v4-step-btn.active')?.focus({ preventScroll: true });
      }
    });

    $('#v4BrandReset')?.addEventListener('click', resetToFrontPage);
    $('#v4HomeIconBtn')?.addEventListener('click', resetToFrontPage);

    const searchInput = $('#v4SearchInput');
    const searchClear = $('#v4SearchClear');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        state.searchTerm = searchInput.value;
        if (state.activePage !== 'today') {
          switchPage('today');
        } else {
          applyFilters();
        }
      });
    }
    if (searchClear) {
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        state.searchTerm = '';
        applyFilters();
        searchInput.focus();
      });
    }

    // Left Navigation Drawer controls
    $('#v4MenuBtn')?.addEventListener('click', openNavDrawer);
    $('#v4NavClose')?.addEventListener('click', () => closeNavDrawer(true));
    $('#v4NavBackdrop')?.addEventListener('click', () => closeNavDrawer(true));

    $('#v4DrawerSearchForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = ($('#v4DrawerSearchInput')?.value || '').trim();
      state.searchTerm = val;
      if (searchInput) searchInput.value = val;
      closeNavDrawer(false);
      switchPage('today');
    });

    // Utility buttons for vCard modal (Header utility bar, Drawer, Footer, Floating Widget)
    ['#v4TopVCardBtn', '#v4FooterVCardBtn'].forEach((sel) => {
      $(sel)?.addEventListener('click', openVCardModal);
    });
    $('#v4OpenVCardBtn')?.addEventListener('click', () => {
      closeNavDrawer(false);
      openVCardModal();
    });
    $('#v4FloatVCard')?.addEventListener('click', () => {
      $('#v4FloatWidget')?.classList.remove('is-open');
      $('#v4FabToggleBtn')?.setAttribute('aria-expanded', 'false');
      openVCardModal();
    });

    // Theme toggle (Drawer button)
    $('#v4ThemeToggleBtn')?.addEventListener('click', toggleTheme);

    // Welcome modal controls
    $('#v4OpenWelcomeBtn')?.addEventListener('click', () => {
      closeNavDrawer(false);
      openWelcomeModal();
    });
    $('#v4WelcomeClose')?.addEventListener('click', () => closeWelcomeModal(true, true));
    $('#v4WelcomeBackdrop')?.addEventListener('click', () => closeWelcomeModal(true, true));
    $('#v4WelcomeExploreBtn')?.addEventListener('click', () => closeWelcomeModal(true, true));
    $('#v4WelcomeContactBtn')?.addEventListener('click', () => {
      closeWelcomeModal(true, false);
      openVCardModal();
    });

    // Right Detail Drawer
    $('#v4DrawerClose')?.addEventListener('click', () => closeDrawer(true));
    $('#v4DrawerBackdrop')?.addEventListener('click', () => closeDrawer(true));

    // Header "Đăng ký Bản tin" CTA -> Chuyển sang Trang 02 (Bản tin & Đăng ký)
    $('#v4SubscribeBtn')?.addEventListener('click', () => {
      switchPage('newsletter');
    });

    // Newsletter subscribe forms (Trang 02, Welcome Modal & Footer Community CTA Band) -> Google Apps Script Webhook
    bindNewsletterForm('#v4NlForm', '#v4NlEmailInput', '#v4NlFeedback', 'Bnews V4 Tab 02 (Top Hero)');
    bindNewsletterForm('#v4WelcomeNlForm', '#v4WelcomeNlInput', '#v4WelcomeNlFeedback', 'Bnews V4 Welcome Modal');
    bindNewsletterForm('#v4FooterNlForm', '#v4FooterNlInput', '#v4FooterNlFeedback', 'Bnews V4 Community Band (Footer)');

    // vCard Modal controls & QR Tabs & Save/Copy actions
    $$('[data-vcard-tab]').forEach((btn) => {
      btn.addEventListener('click', () => switchVCardTab(btn.dataset.vcardTab));
    });
    $('#v4DownloadVCardBtn')?.addEventListener('click', downloadVCard);
    $('#v4CopyVCardLinkBtn')?.addEventListener('click', (e) => copyVCardLink(e.currentTarget));
    $('#v4VCardClose')?.addEventListener('click', () => closeVCardModal(true));
    $('#v4VCardBackdrop')?.addEventListener('click', () => closeVCardModal(true));

    // Floating Quick-Connect Widget toggle & Back to Top
    $('#v4FabToggleBtn')?.addEventListener('click', (e) => {
      e.stopPropagation();
      const fw = $('#v4FloatWidget');
      if (!fw) return;
      const open = fw.classList.toggle('is-open');
      e.currentTarget.setAttribute('aria-expanded', String(open));
    });
    $('#v4BackToTopBtn')?.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', updateBackToTopState, { passive: true });
    updateBackToTopState();

    // Sync URL hash changes
    window.addEventListener('hashchange', () => {
      const h = (window.location.hash || '').replace('#', '').toLowerCase();
      if (['today', 'newsletter', 'analysis', 'b2b'].includes(h)) {
        switchPage(h, { syncHash: false });
      }
    });
  }

  async function init() {
    let savedTheme = localStorage.getItem('site_theme');
    const legacy = localStorage.getItem('ms-theme');
    if (!savedTheme && (legacy === 'dark' || legacy === 'light')) {
      savedTheme = legacy;
      localStorage.setItem('site_theme', savedTheme);
    }
    if (legacy !== null) localStorage.removeItem('ms-theme');
    if (savedTheme !== 'dark' && savedTheme !== 'light') {
      savedTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    applyTheme(savedTheme);

    const data = await loadEditionData();
    if (!data) {
      const mount = $('#v4FrontPageView');
      if (mount) {
        mount.innerHTML = '<div class="v4-container" style="padding:48px 24px;"><p>Không thể tải dữ liệu ấn bản.</p></div>';
      }
      return;
    }

    // Rewrite internal links so trailing-slash-free replaceState URL never breaks relative paths
    if (window.location.protocol !== 'file:') {
      $$('a[href$="newsletter-preview.html"]').forEach((a) => {
        a.setAttribute('href', `${CURRENT_DIR_BASE}newsletter-preview.html`);
      });
      $$('a[href$="../index.html"]').forEach((a) => {
        if (!a.classList.contains('v4-anchor-link')) {
          a.setAttribute('href', PORTFOLIO_HOME_URL);
        }
      });
    }

    state.data = data;
    (data.eligibleNewsList || []).forEach((item) => {
      if (item.eventId) state.newsById[item.eventId] = item;
    });
    updateSeoAndStructuredData();

    try {
      const q = new URLSearchParams(window.location.search).get('q');
      if (q && q.trim()) {
        state.searchTerm = q.trim();
        const searchInput = $('#v4SearchInput');
        if (searchInput) searchInput.value = state.searchTerm;
      }
    } catch (_) {}

    renderMasthead();
    renderPulseStrip();
    renderFrontPage();
    renderCategoryClusters();
    renderMacroMicro();
    renderFintechCorner();
    renderB2BPage();
    bindGlobalEvents();
    initPwaAndWebPush();

    const hashPage = (window.location.hash || '').replace('#', '').toLowerCase();
    const initialPage = ['today', 'newsletter', 'analysis', 'b2b'].includes(hashPage) ? hashPage : 'today';
    switchPage(initialPage);

    try {
      if (!localStorage.getItem(WELCOME_STORAGE_KEY)) {
        setTimeout(() => {
          const anyModalOpen = ['#v4Drawer', '#v4NavDrawer', '#v4VCardModal'].some((sel) => {
            const el = $(sel);
            return el && !el.hidden;
          });
          if (!anyModalOpen) openWelcomeModal();
        }, 450);
      }
    } catch (_) {}
  }

  // ─── PWA & WEB PUSH NOTIFICATIONS (FIREBASE FCM + FIRESTORE) ────────────────
  async function hashTokenId(token) {
    if (window.crypto?.subtle) {
      const buf = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(token));
      return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
    }
    return token.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 64);
  }

  async function subscribeFirebasePush(pushCfg, bellBtn) {
    const fbCfg = pushCfg.firebaseConfig;
    const vapidKey = (pushCfg.vapidKey || '').trim();
    if (!fbCfg || !fbCfg.apiKey || !vapidKey) return { ok: false, reason: 'missing_vapid' };

    const [{ initializeApp, getApps }, { getMessaging, getToken }, { getFirestore, doc, setDoc, serverTimestamp }] =
      await Promise.all([
        import('https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js'),
        import('https://www.gstatic.com/firebasejs/11.1.0/firebase-messaging.js'),
        import('https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js'),
      ]);

    const app = getApps().length ? getApps()[0] : initializeApp(fbCfg);
    const messaging = getMessaging(app);
    const db = getFirestore(app);

    const swReg = await navigator.serviceWorker.register(
      pushCfg.serviceWorkerPath || `${CURRENT_DIR_BASE}firebase-messaging-sw.js`,
      { scope: pushCfg.scope || CURRENT_DIR_BASE }
    );

    const token = await getToken(messaging, { vapidKey, serviceWorkerRegistration: swReg });
    if (!token) return { ok: false, reason: 'no_token' };

    const ua = navigator.userAgent || '';
    const isIos = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    const isAndroid = /Android/i.test(ua);
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    const platform = isIos && isStandalone ? 'ios_pwa' : isAndroid ? 'android' : /Mac|Windows|Linux/i.test(ua) ? 'desktop' : 'web';

    const tokenId = await hashTokenId(token);
    await setDoc(doc(db, 'fcm_tokens', tokenId), {
      token,
      platform,
      userAgent: ua.slice(0, 280),
      updatedAt: serverTimestamp(),
    });

    if (bellBtn) {
      bellBtn.classList.add('is-subscribed');
      bellBtn.title = 'Đã bật thông báo đẩy Bnews (Firebase FCM)';
    }
    return { ok: true, token };
  }

  async function initPwaAndWebPush() {
    if ('serviceWorker' in navigator && window.location.protocol !== 'file:') {
      try {
        await navigator.serviceWorker.register(`${CURRENT_DIR_BASE}sw.js`, {
          scope: CURRENT_DIR_BASE,
        });
      } catch (_) {}
    }

    let pushCfg = {};
    try {
      const resp = await fetch(`${CURRENT_DIR_BASE}push-config.json?v=${Date.now()}`, { cache: 'no-store' });
      if (resp.ok) pushCfg = await resp.json();
    } catch (_) {}

    const vapidKey = (pushCfg.vapidKey || '').trim();
    const bellBtn = $('#v4PushNotifyBtn');

    if (bellBtn && typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      bellBtn.classList.add('is-subscribed');
      if (vapidKey && window.location.protocol !== 'file:') {
        subscribeFirebasePush(pushCfg, bellBtn).catch(() => {});
      }
    }

    if (bellBtn) {
      bellBtn.addEventListener('click', async () => {
        const ua = window.navigator.userAgent || '';
        const isIos = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

        if (isIos && !isStandalone) {
          openDrawer(
            'Bật thông báo đẩy trên iPhone',
            `
              <span class="v4-crimson-tag">HƯỚNG DẪN IOS (APPLE PWA)</span>
              <h2 class="v4-drawer-title">Cài Bnews ra Màn hình chính để nhận thông báo đẩy</h2>
              <p class="v4-drawer-meta">Apple yêu cầu trang web phải được thêm vào Màn hình chính trước khi gửi thông báo đẩy khi đóng trình duyệt.</p>
              <div class="v4-drawer-block">
                <div class="v4-drawer-block-label">BƯỚC 1 · CHIA SẺ</div>
                <p class="v4-drawer-block-text">Nhấn biểu tượng <strong>Chia sẻ (Share)</strong> ở thanh dưới cùng của Safari.</p>
              </div>
              <div class="v4-drawer-block">
                <div class="v4-drawer-block-label">BƯỚC 2 · THÊM VÀO MÀN HÌNH CHÍNH</div>
                <p class="v4-drawer-block-text">Chọn <strong>Thêm vào Màn hình chính (Add to Home Screen)</strong> → bấm <strong>Thêm</strong>.</p>
              </div>
              <div class="v4-drawer-block">
                <div class="v4-drawer-block-label">BƯỚC 3 · CHO PHÉP THÔNG BÁO</div>
                <p class="v4-drawer-block-text">Mở biểu tượng <strong>Bnews</strong> vừa tạo trên Màn hình chính và nhấn nút chuông thông báo một lần để kích hoạt.</p>
              </div>
            `
          );
          return;
        }

        if (typeof Notification === 'undefined') {
          openDrawer('Thông báo đẩy Web Push', '<p class="v4-drawer-block-text">Trình duyệt hiện tại chưa hỗ trợ Web Push Notifications.</p>');
          return;
        }

        const perm = await Notification.requestPermission();
        if (perm !== 'granted') {
          openDrawer('Thông báo đẩy Web Push', '<p class="v4-drawer-block-text">Bạn chưa cấp quyền thông báo cho trình duyệt. Hãy bật lại quyền Notifications trong cài đặt trình duyệt để nhận ấn bản mới mỗi sáng.</p>');
          return;
        }

        if (vapidKey && window.location.protocol !== 'file:') {
          try {
            const res = await subscribeFirebasePush(pushCfg, bellBtn);
            if (res.ok) {
              openDrawer(
                'Đã bật thông báo đẩy Bnews',
                `
                  <span class="v4-crimson-tag">FIREBASE CLOUD MESSAGING</span>
                  <h2 class="v4-drawer-title">Đăng ký nhận thông báo thành công</h2>
                  <p class="v4-drawer-block-text">Thiết bị của bạn đã được lưu an toàn. Bạn sẽ nhận được thông báo ngay khi ấn bản tài chính mới xuất bản mỗi sáng, kể cả khi đóng trình duyệt.</p>
                `
              );
              return;
            }
          } catch (_) {}
        }

        bellBtn.classList.add('is-subscribed');
        openDrawer(
          'Thông báo đẩy Firebase (PWA)',
          `
            <span class="v4-crimson-tag">CHỜ HOÀN TẤT VAPID KEY</span>
            <h2 class="v4-drawer-title">Trình duyệt đã cấp quyền · Chờ gắn VAPID Key</h2>
            <p class="v4-drawer-meta">Project Firebase: <strong>bnews-11b05</strong></p>
            <div class="v4-drawer-block">
              <div class="v4-drawer-block-label">CẤU HÌNH CUỐI</div>
              <p class="v4-drawer-block-text">Bật Cloud Firestore API và tạo Web Push certificate (VAPID Key) trong Firebase Console rồi điền vào <code>fintech-intelligence/push-config.json</code>.</p>
            </div>
          `
        );
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
