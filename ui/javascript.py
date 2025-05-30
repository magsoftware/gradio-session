"""
JavaScript code as a string that defines a fetch interceptor for handling 401
Unauthorized responses.

This interceptor wraps the native `window.fetch` function to:
- Log all outgoing requests and their URLs.
- Log the status of all responses.
- If a response has a 401 status code:
    - Attempts to parse the response body as JSON.
    - If the JSON contains a `redirect_to` field, logs the redirect URL and
      redirects the browser to that URL after a short delay.
    - Returns a dummy 200 OK response with a "Redirecting..." message to
      prevent UI errors during the redirect.
- If the response is not a 401, or if parsing fails, returns the original
  response.

Intended for use in a frontend application to handle authentication redirects
automatically.o

Used in main Gradio gr.Blocks statement.
"""
redirect_js = """
() => {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        const [resource, config] = args;
        const url = typeof resource === "string" ? resource : resource.url;
        console.log("[Interceptor] Request to:", url);

        const response = await originalFetch(...args);
        console.log("[Interceptor] Response status:", response.status);

        if (response.status === 401) {
            try {
                const data = await response.clone().json();
                console.log("[Interceptor] 401 data:", data);
                if (data.redirect_to) {
                    console.log("[Interceptor] Redirecting to:", data.redirect_to);
                    setTimeout(() => {
                        window.location.href = data.redirect_to;
                    }, 1000); // 1000 ms delay before redirect
                    // Return empty response to avoid UI error
                    return new Response(JSON.stringify({ detail: "Redirecting..." }), {
                        status: 200,
                        headers: { "Content-Type": "application/json" }
                    });
                }
            } catch (e) {
                console.warn("[Interceptor] Failed to parse JSON:", e);
            }
        }

        return response;
    };
}
"""
