<script lang="ts">
	import '@picocss/pico';
	import '../app.css';

	let { children } = $props();
</script>
<header class="container-fluid">
	<nav>
		<ul class="logo"><li><a href="/">My logo</a></li></ul>

		<ul class="navigation-list">
			<li><a href="/">home</a></li>
			<li><a href="/about">about</a></li>
		</ul>
		<ul class="navigation-login">
			<li>
				<a href="/login">
					<button class="login-button">Login</button>
				</a>
			</li>
		</ul>
	</nav>
</header>

{@render children()}
