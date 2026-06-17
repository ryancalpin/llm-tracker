export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/llms')) {
      return new Response('Not found', { status: 404 });
    }
    const target = 'https://llm-tracker.pages.dev' + url.pathname.replace(/^\/llms/, '/') + url.search;
    const response = await fetch(target, {
      method: request.method,
      headers: request.headers,
    });
    return response;
  },
}