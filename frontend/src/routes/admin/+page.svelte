<script lang="ts">
	import { enhance } from '$app/forms';
	import AdminLoginForm from '$lib/AdminLoginForm.svelte';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let start_loading_form: HTMLFormElement;

	function confirmStartLoad() {
		const confirmed = window.confirm(
			'Are you sure you want to start manual loading?\n!! CAN TAKE A FEW MINUTES !!  '
		);
		if (confirmed) {
			start_loading_form.submit();
		}
	}
</script>

{#if form?.error}
	<div class="info error-block">
		<div class="info-title"><b>Error:</b> {form?.error}</div>
		<div class="info-message">{form?.errorMessage}</div>
	</div>
{/if}
{#if form?.logged}
	<div class="info success-block">
		<div class="info-message">Logged successfully</div>
	</div>
{/if}
<main class="container">
	<h1 style="text-align: center;">Server Administration</h1>
	<hr />
	{#if data.admin_token}
		<div class="logout">
			<h3>Logged in as "<i>{data.admin_user}</i>"</h3>
			<form method="POST" action="?/logout">
				<button type="submit"> Log out </button>
			</form>
		</div>
		<hr />

		<div class="status">
			<h3>Current operation</h3>
			{#await data.operation}
				<article aria-busy="true"></article>
			{:then operation}
				{#if operation}
					<article>{operation}</article>
				{:else}
					<article>No operation in progress</article>
				{/if}
			{/await}

			<p><i></i></p>
		</div>
		<hr />
		<div class="execute">
			<h3>Load players stats</h3>
			<p>
				Load the latest statistics of hockey players from hockey manager website into the database
			</p>
			
			<form method="POST" action="?/start_stats_loading" bind:this={start_loading_form}>
				<button onclick={confirmStartLoad}>Start load</button>
				{#if form?.started}
				<div class="info success-block">
					<div class="info-message">Started loading the players</div>
				</div>
			{/if}
			</form>
		</div>
	{:else}
		<AdminLoginForm />
	{/if}
</main>
