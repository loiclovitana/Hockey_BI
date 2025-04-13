<script>
	import AdminLoginForm from '$lib/AdminLoginForm.svelte';
	let { data } = $props();
</script>

<main class="container">
	<h1 style="text-align: center;">Server Administration</h1>
	<hr />
	{#if data.admin_token}
		<h2>Logged in as "<i>{data.admin_user}</i>"</h2>
		<form method="POST" action="?/logout">
			<button type="submit"> Log out </button>
		</form>
	{:else}
		<AdminLoginForm />
	{/if}
</main>
