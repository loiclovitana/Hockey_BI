import type { PageServerLoad } from './$types';
import type {Actions } from './$types';

import { adminLogin } from '$lib/hmTrackerApiClient'

export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('admin_token');
    const admin_user = cookies.get('admin_user');
    return { admin_token: token, admin_user: admin_user };
};

export const actions = {
    login: async ({ cookies, request }) => {
        const data: FormData = await request.formData();
        const admin_user: string | undefined = data.get('user')?.toString();
        const password: string | undefined = data.get('password')?.toString();

        if (admin_user === undefined || password === undefined) {
            return { logged: false };
        }

        const tokenResponse = await adminLogin(admin_user, password);
        if (!tokenResponse.ok) {
            return { success: false };
        }

        let tokenData = await tokenResponse.json()
        let token = tokenData.access_token;
        cookies.set('admin_token', token, { path: '/admin' });
        cookies.set('admin_user', admin_user, { path: '/admin' });
        return { success: true };
    },
    logout:async({ cookies, request }) =>{
        cookies.delete('admin_token',{ path: '/admin' });
        cookies.delete('admin_user',{ path: '/admin' });
    }
} satisfies Actions;

