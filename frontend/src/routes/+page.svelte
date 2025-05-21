<main class="container">
	<div class="hm-login">
		<h2>Log in</h2>
		<small><i>Please use Hockey Manager Credentials</i></small>

		<form method="POST" action="?/start">
			<input
				type="text"
				name="user"
				placeholder="User"
				aria-label="User"
				autoComplete="username"
				required
			/>
			<input
				type="password"
				name="password"
				placeholder="Password"
				aria-label="Password"
				autoComplete="current-password"
				required
			/>
			<fieldset>
				<label for="remember">
					<input type="checkbox" role="switch" id="remember" name="remember" />
					Remember me
				</label>
			</fieldset>
			<button type="submit"> Start </button>
		</form>
	</div>
</main>
