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
                    }, 1000);
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
