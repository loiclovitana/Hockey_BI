import { fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { Actions } from './$types';

import { adminLogin, getOperation, startStatsLoading } from '$lib/hmTrackerApiClient'

export const load: PageServerLoad = async ({ cookies }) => {
    const admin_token: string | undefined = cookies.get('admin_token');
    const admin_user: string | undefined = cookies.get('admin_user');
    const operation: Promise<string> = admin_token === undefined ? new Promise(() => '') : getOperation(admin_token);
    return { admin_token: admin_token, admin_user: admin_user, operation: operation };
};

export const actions = {
    login: async ({ cookies, request }) => {
        logRequest(request);
        if (cookies.get('admin_token')) {
            return fail(403, { error: 403, errorMessage: "User is already logged" });
        }

        const data: FormData = await request.formData();
        const admin_user: string | undefined = data.get('user')?.toString();
        const password: string | undefined = data.get('password')?.toString();

        if (admin_user === undefined || password === undefined) {
            fail(401, { error: 401, errorMessage: "The user or the password was not provided for login" });
        }

        const tokenResponse = await adminLogin(admin_user as string, password as string);
        if (!tokenResponse.ok) {
            return fail(tokenResponse.status, { error: tokenResponse.status, errorMessage: await tokenResponse.text() });
        }

        let tokenData = await tokenResponse.json()
        let token = tokenData.access_token;
        cookies.set('admin_token', token, { path: '/admin' });
        cookies.set('admin_user', admin_user as string, { path: '/admin' });
        return { logged: true };
    },
    logout: async ({ cookies, request }) => {
        logRequest(request);
        cookies.delete('admin_token', { path: '/admin' });
        cookies.delete('admin_user', { path: '/admin' });
    },
    start_stats_loading: async ({ cookies, request }) => {
        logRequest(request);
        const admin_token: string | undefined = cookies.get('admin_token');
        if (admin_token === undefined) {
            fail(401, {
                error: 401,
                errorMessage: 'Admin need to be logged in to execute operation',
            });
        }
        const response =  await startStatsLoading(admin_token as string);
        if (!response.ok) {
            return fail(response.status, { error: response.status, errorMessage: await response.text() });
        }
        return {started:true};
    }
} satisfies Actions;

function logRequest(request:Request){
    const now = new Date();
    let message : string =`${now.toLocaleTimeString("fr-CH")} [${request.method}] - ${request.url}`;
    console.info(message);
}

