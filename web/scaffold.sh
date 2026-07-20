#!/bin/bash
# Run from TradeIQ/ project root, after `npx create-next-app@latest web ...`
set -e


# Route groups
mkdir -p "app/(auth)/welcome" "app/(auth)/login" "app/(auth)/signup"
mkdir -p "app/(app)/market" "app/(app)/news" "app/(app)/profile"

touch "app/(auth)/layout.tsx"
touch "app/(auth)/welcome/page.tsx"
touch "app/(auth)/login/page.tsx"
touch "app/(auth)/signup/page.tsx"

touch "app/(app)/layout.tsx"
touch "app/(app)/page.tsx"
touch "app/(app)/market/page.tsx"
touch "app/(app)/news/page.tsx"
touch "app/(app)/profile/page.tsx"

# Components
mkdir -p components
touch components/NavShell.tsx
touch components/Icons.tsx
touch components/Charts.tsx
touch components/MetricCard.tsx
touch components/AuthForm.tsx

# Lib
mkdir -p lib
touch lib/api.ts
touch lib/ThemeContext.tsx
touch lib/AuthContext.tsx

# CI
mkdir -p .github/workflows
touch .github/workflows/ci.yml

echo "Scaffold complete. Folder structure:"
find app components lib .github -type f | sort