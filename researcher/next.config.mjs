const api = process.env.BINTANONG_REVIEW_API_ORIGIN ?? 'http://127.0.0.1:8765';
const address = new URL(api);
if (address.protocol !== 'http:' || address.hostname !== '127.0.0.1' || !address.port
    || address.pathname !== '/' || address.search || address.hash || address.username || address.password) {
  throw new Error('The review API must be a loopback origin.');
}
export default {
  distDir: 'audit-evidence/next',
  outputFileTracingRoot: import.meta.dirname,
  allowedDevOrigins: ['127.0.0.1', 'localhost'],
  async headers() {
    const policy = `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; connect-src 'self' ws://127.0.0.1:*; frame-ancestors 'none'; base-uri 'none'; form-action 'none'`;
    // the source PDFs are framed by the review page itself (the browser's PDF viewer); nothing else may frame them
    const framedPdf = { key: 'Content-Security-Policy', value: policy.replace("frame-ancestors 'none'", "frame-ancestors 'self'") };
    return [{ source: '/:path*', headers: [
      { key: 'Referrer-Policy', value: 'no-referrer' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Cache-Control', value: 'no-store' },
      { key: 'Content-Security-Policy', value: policy },
    ] }, { source: '/review/api/source/:identity', headers: [framedPdf] },
    { source: '/review/api/knowledge/pdf', headers: [framedPdf] }];
  },
};
