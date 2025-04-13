
<h2>Log in</h2>
<small><i>Administrator privilege required</i></small>

<form method="POST" action="?/login">
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
    <button type="submit"> Login </button>
</form>