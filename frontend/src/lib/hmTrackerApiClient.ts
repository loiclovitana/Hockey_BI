import { PUBLIC_HM_TRACKER_API_URL } from '$env/static/public';


export async function adminLogin(username: string, password: string): Promise<Response> {
    try {
        const body = new URLSearchParams({
            grant_type: 'password',
            username: username,
            password: password,
            scope: '',
            client_id: 'string',
            client_secret: 'string',
          });

        const response = await fetch(PUBLIC_HM_TRACKER_API_URL + '/admin/login', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: body.toString()
        })
        return response;
    }
    catch (error) {

        let message: string = 'Unknown Error'
        if (error instanceof Error) { message = error.message; }
        console.error("Error during login:", error);
        var errorResponse = new Response(message, { status: 400 });
        return errorResponse;
    }
}