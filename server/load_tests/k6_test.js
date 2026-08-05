import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50, // user
  duration: '10s',
};

export default function () {
  const alias = 'Tutorial_Django'; 
  
  const url = `http://127.0.0.1:8000/${alias}`;
  
  // redirects: 0 mematikan fitur pindah halaman otomatis.
  // K6 hanya akan fokus menghitung kecepatan server FastAPI Anda merespons 302 Found.
  const res = http.get(url, { redirects: 0 });

  // Validasi bahwa response statusnya 302
  check(res, {
    'status is 302': (r) => r.status === 302,
  });
  
  // Memberikan napas yang sangat tipis agar tidak menghabiskan RAM komputer Anda sendiri
  sleep(0.01);
}
