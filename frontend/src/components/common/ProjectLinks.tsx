import { Link, Stack, Typography } from "@mui/material";
import { GitHub } from "@mui/icons-material";

const projectLinks = [
  {
    label: "GitHub repository",
    href: "https://github.com/loiclovitana/Hockey_BI",
    icon: GitHub,
  },
  {
    label: "My website",
    href: "https://loic.vandenberghe.ch",
    icon: null,
  },
];

export function LoginProjectLinks() {
  return (
    <Stack
      component="nav"
      aria-label="Project links"
      direction="row"
      spacing={1.5}
      divider={
        <Typography component="span" color="text.disabled" aria-hidden="true">
          ·
        </Typography>
      }
      sx={{ mt: 4, mb: 2, alignItems: "center", justifyContent: "center" }}
    >
      {projectLinks.map(({ label, href, icon: Icon }) =>
        href ? (
          <Link
            key={label}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            variant="body2"
            color="text.secondary"
            underline="hover"
            aria-label={`${label} (opens in a new tab)`}
            sx={{ display: "inline-flex", alignItems: "center", gap: 0.75 }}
          >
            {Icon && <Icon sx={{ fontSize: 16 }} />}
            {label}
          </Link>
        ) : (
          <Typography
            key={label}
            component="span"
            variant="body2"
            color="text.disabled"
            aria-disabled="true"
          >
            {label}
          </Typography>
        ),
      )}
    </Stack>
  );
}
