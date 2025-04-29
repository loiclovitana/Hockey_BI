import { PUBLIC_HM_TRACKER_API_URL } from '$env/static/public';

const TIMEOUT = 5000;

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
            body: body.toString(),
            signal: AbortSignal.timeout(TIMEOUT) 
        })
        return response;
    }
    catch (error) {
        return handleError(error);
    }
}


export async function getOperation(admin_token: string): Promise<string> {
    try {
        const response = await fetch(PUBLIC_HM_TRACKER_API_URL + '/admin/operation', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                Authorization: 'Bearer ' + admin_token
            },
            signal: AbortSignal.timeout(TIMEOUT)
        });
        if (response.ok) {
            return response.text();
        } else if (response.status == 404) {
            return "";

        } else {
            console.error(response.status, response.statusText)
            return response.status.toString() + ' ' + response.statusText;
        }
    } catch (error) {
        return handleError(error).text();
    }
}

export async function startStatsLoading(admin_token: string): Promise<Response> {
    try {
        const response = await fetch(PUBLIC_HM_TRACKER_API_URL + '/admin/load/start', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                Authorization: 'Bearer ' + admin_token
            },
            signal: AbortSignal.timeout(TIMEOUT) 
        });
        if (response.ok) {
            return response;
        } else {
            console.error(response.status, response.statusText)
            return response;
        }
    } catch (error) {
        return handleError(error);
    }
}

function handleError(error: unknown) {
    let message: string = 'Unknown Error'
    if (error instanceof Error) {
        message = error.message;
    }

    console.error(error);
    var errorResponse = new Response(message, { status: 400 });
    return errorResponse;
}