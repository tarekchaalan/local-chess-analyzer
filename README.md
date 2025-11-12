<div id="top">

<!-- HEADER STYLE: MODERN -->
<div align="center" style="width: 100%;">

<img src="./frontend/src/assets/logo.svg" width="35%" style="display: block; margin: 0 auto;" alt="Project Logo"/>

# CHESS ANALYSIS (LOCAL)

<em><em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/tarekchaalan/local-chess-analyzer?style=flat&logo=opensourceinitiative&logoColor=white&color=#FFFFFF" alt="license">
<img src="https://img.shields.io/github/last-commit/tarekchaalan/local-chess-analyzer?style=flat&logo=git&logoColor=white&color=#FFFFFF" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/tarekchaalan/local-chess-analyzer?style=flat&color=#FFFFFF" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/tarekchaalan/local-chess-analyzer?style=flat&color=#FFFFFF" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/npm-CB3837.svg?style=flat&logo=npm&logoColor=white" alt="npm">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/Svelte-FF3E00.svg?style=flat&logo=Svelte&logoColor=white" alt="Svelte">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=flat&logo=JavaScript&logoColor=black" alt="JavaScript">
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=flat&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
<br>
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/TypeScript-3178C6.svg?style=flat&logo=TypeScript&logoColor=white" alt="TypeScript">
<img src="https://img.shields.io/badge/C-A8B9CC.svg?style=flat&logo=C&logoColor=black" alt="C">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/Vite-646CFF.svg?style=flat&logo=Vite&logoColor=white" alt="Vite">
<img src="https://img.shields.io/badge/CSS-663399.svg?style=flat&logo=CSS&logoColor=white" alt="CSS">

</div>
</div>
<br clear="right">

---

## Table of Contents

<details>
<summary>Table of Contents</summary>

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

</details>

---

## Overview


This project is a privacy‑first, fully local toolkit for exploring your online chess games. It syncs games from Chess.com into a lightweight SQLite database and analyzes them on your machine using the Stockfish engine—no cloud services or data sharing required.

- Svelte frontend: fast SPA with interactive boards, filters, and game browsing.
- FastAPI backend: REST endpoints for sync, analysis, stats, and DB management.
- Local engine analysis: configurable depth/time, threads, and hash usage.
- Simple ops: one‑command Docker setup or separate frontend/backend dev flows.
- Portable data: download/upload the database for backups or migration.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Microservices: Frontend (Svelte) & Backend (FastAPI)</li><li>Containerized with Docker</li><li>CI/CD with GitHub Actions</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Consistent use of TypeScript and JavaScript</li><li>Adheres to modern coding standards</li><li>Static analysis tools not specified</li></ul> |
| 📄 | **Documentation** | <ul><li>Comprehensive Docker setup in `docker-compose.yml`</li><li>Basic project structure outlined in `README.md`</li><li>Licensing info in `unlicence`</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Stockfish for chess analysis</li><li>Vite for frontend tooling</li><li>SQLAlchemy for database interactions</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Separation of frontend and backend</li><li>Modular Svelte components</li><li>Backend API endpoints structured by functionality</li></ul> |
| 🧪 | **Testing**       | <ul><li>No explicit testing framework mentioned</li><li>Potential for unit tests with Pytest and Jest</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Efficient use of Stockfish binary</li><li>FastAPI for high-performance backend</li><li>Potential bottlenecks in synchronous operations</li></ul> |
| 🛡️ | **Security**      | <ul><li>Basic security practices in Docker setup</li><li>No explicit mention of security audits</li><li>Potential vulnerabilities in dependencies</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Frontend: Svelte, Vite, `@sveltejs/vite-plugin-svelte`</li><li>Backend: FastAPI, SQLAlchemy, `python-chess`</li><li>Managed via npm and pip</li></ul> |
| 🚀 | **Scalability**   | <ul><li>Scalable microservices architecture</li><li>Docker for easy deployment</li><li>Potential horizontal scaling with container orchestration</li></ul> |


---

## Project Structure

```sh
└── local-chess-analyzer/
    ├── .github
    │   └── workflows
    │       ├── push-images.yml
    │       ├── release-images.yml
    │       └── release.yml
    ├── README.md
    ├── backend
    │   ├── Dockerfile
    │   ├── app
    │   │   ├── api
    │   │   ├── crud
    │   │   ├── db
    │   │   ├── main.py
    │   │   └── services
    │   └── requirements.txt
    ├── data
    │   ├── .gitkeep
    │   └── analysis
    │       └── .gitkeep
    ├── docker-compose.yml
    ├── frontend
    │   ├── .gitignore
    │   ├── .vscode
    │   │   └── extensions.json
    │   ├── Dockerfile
    │   ├── index.html
    │   ├── jsconfig.json
    │   ├── nginx.conf
    │   ├── package-lock.json
    │   ├── package.json
    │   ├── public
    │   │   └── logo.svg
    │   ├── src
    │   │   ├── App.svelte
    │   │   ├── app.css
    │   │   ├── assets
    │   │   ├── lib
    │   │   ├── main.js
    │   │   └── vite-env.d.ts
    │   ├── svelte.config.js
    │   └── vite.config.js
    ├── scripts
    │   ├── dev.sh
    │   ├── run-images.ps1
    │   └── run-images.sh
    └── stockfish/
```

### Project Index

<details open>
	<summary><b><code>LOCAL-CHESS-ANALYZER/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/docker-compose.yml'>docker-compose.yml</a></b></td>
					<td style='padding: 8px;'>- The <code>docker-compose.yml</code> file orchestrates the deployment of a multi-service application, integrating a FastAPI backend and a Svelte frontend served by Nginx<br>- It facilitates seamless communication between the frontend and backend by defining service dependencies and port mappings<br>- This setup ensures the application is consistently available and easily scalable, enhancing the overall architectures robustness and maintainability.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- frontend Submodule -->
	<details>
		<summary><b>frontend</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ frontend</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/jsconfig.json'>jsconfig.json</a></b></td>
					<td style='padding: 8px;'>- Configuration of TypeScript settings in the frontend/jsconfig.json file optimizes the development environment for a Svelte-based project<br>- It ensures compatibility with modern JavaScript features, enhances module resolution, and facilitates accurate source mapping<br>- By enabling type checking in JavaScript and Svelte files, it improves code reliability and maintainability, while also supporting seamless integration with Vite and other modern tooling.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/svelte.config.js'>svelte.config.js</a></b></td>
					<td style='padding: 8px;'>- Configure the Svelte framework to utilize Vites preprocessing capabilities, enhancing the build process for the frontend component of the project<br>- By integrating Vites preprocessing, the setup ensures efficient handling of Svelte files, optimizing them for development and production environments<br>- This configuration is a critical part of the frontend architecture, streamlining the transformation and compilation of Svelte components within the overall project structure.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/index.html'>index.html</a></b></td>
					<td style='padding: 8px;'>- The <code>index.html</code> file serves as the entry point for the Chess Analyzers frontend, setting up the initial HTML structure and linking essential resources<br>- It defines the documents metadata, including title and description, and integrates the main JavaScript module to render the application<br>- This file is crucial for initializing the user interface, enabling users to analyze chess games using the Stockfish engine.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/Dockerfile'>Dockerfile</a></b></td>
					<td style='padding: 8px;'>- Facilitate the deployment of the frontend application by defining a multi-stage Docker build process<br>- Initially, a Node.js environment compiles the application, followed by an Nginx server configuration to serve the built static files<br>- This approach optimizes the build size and enhances performance, ensuring the frontend is efficiently packaged and ready for production within the broader architecture of the project.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/vite.config.js'>vite.config.js</a></b></td>
					<td style='padding: 8px;'>- Configures the Vite build tool to integrate with Svelte, enabling efficient development and bundling of the frontend components within the project<br>- By leveraging the Vite plugin for Svelte, it ensures optimized performance and a streamlined development experience<br>- This setup is crucial for maintaining a responsive and dynamic user interface, aligning with the projects architecture to deliver a seamless frontend experience.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/package-lock.json'>package-lock.json</a></b></td>
					<td style='padding: 8px;'>- The <code>frontend/package-lock.json</code> file is a crucial component of the projects frontend architecture<br>- Its primary purpose is to ensure consistent dependency management by locking the specific versions of all installed packages and their dependencies<br>- This file guarantees that every developer working on the project, as well as any deployment environments, use the exact same package versions, thereby minimizing discrepancies and potential issues related to dependency conflicts<br>- It plays a vital role in maintaining the stability and reliability of the frontend application by providing a snapshot of the entire dependency tree at the time of installation.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/package.json'>package.json</a></b></td>
					<td style='padding: 8px;'>- The frontend/package.json file orchestrates the setup and management of the frontend application within the project<br>- It defines essential scripts for development, building, and previewing the application using Vite<br>- It also specifies dependencies crucial for the frontends functionality, including Svelte for component-based architecture, chess.js and chessground for chess-related features, and svelte-spa-router for single-page application routing.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/nginx.conf'>nginx.conf</a></b></td>
					<td style='padding: 8px;'>- Configure the Nginx server to serve a Single Page Application (SPA) by directing requests to static files and handling routing<br>- It also proxies API requests to the backend service, ensuring seamless integration between the frontend and backend<br>- The configuration includes settings to manage timeouts and headers, optimizing performance and reliability for both static content delivery and API interactions within the project architecture.</td>
				</tr>
			</table>
			<!-- src Submodule -->
			<details>
				<summary><b>src</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ frontend.src</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/app.css'>app.css</a></b></td>
							<td style='padding: 8px;'>- Defines the global styling and theme settings for the Chess Analyzers frontend, ensuring a consistent and visually appealing user interface<br>- Establishes base styles for typography, layout, and interactive elements, while providing a dark theme variant for enhanced user experience<br>- Supports utility classes for common styling needs and ensures responsive design across different devices, contributing to the overall aesthetic and usability of the application.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/App.svelte'>App.svelte</a></b></td>
							<td style='padding: 8px;'>- The <code>App.svelte</code> component serves as the main entry point for the frontend application, orchestrating the user interface and navigation<br>- It initializes the application by checking user settings, applying themes, and conditionally displaying a setup wizard if necessary<br>- It also integrates a router to manage navigation between different views such as Home, Settings, Sync, and Games, ensuring a seamless user experience.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/main.js'>main.js</a></b></td>
							<td style='padding: 8px;'>- Initialize the Svelte application by mounting the main App component to a specified DOM element<br>- Serve as the entry point for the frontend, ensuring that the application is styled with the imported CSS and rendered within the designated HTML container<br>- Facilitate the seamless integration of the Svelte framework into the projects architecture, enabling dynamic and reactive user interfaces.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/vite-env.d.ts'>vite-env.d.ts</a></b></td>
							<td style='padding: 8px;'>- Facilitation of TypeScript support for importing various image file formats in the frontend codebase is achieved through module declarations<br>- By defining modules for image types such as SVG, PNG, JPG, JPEG, GIF, and WEBP, seamless integration and usage of these assets within the Vite-powered development environment is ensured, enhancing the developer experience and maintaining type safety across the application.</td>
						</tr>
					</table>
					<!-- lib Submodule -->
					<details>
						<summary><b>lib</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ frontend.src.lib</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/Counter.svelte'>Counter.svelte</a></b></td>
									<td style='padding: 8px;'>- Counter component provides a simple interactive feature for incrementing a numerical value displayed on the user interface<br>- Serving as a part of the frontend library, it enhances user engagement by allowing real-time updates to the count state<br>- This component is likely used in various parts of the application to demonstrate dynamic state management and user interaction within the broader architecture of the project.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/theme.js'>theme.js</a></b></td>
									<td style='padding: 8px;'>- Facilitates dynamic theme application within the frontend, enabling seamless switching between dark and light modes<br>- Enhances user experience by adjusting the visual presentation based on user preference or system settings<br>- Integrates with the broader architecture by modifying the documents body class, ensuring consistent styling across the application<br>- Provides resilience by handling non-browser contexts gracefully, maintaining functionality across diverse environments.</td>
								</tr>
							</table>
							<!-- components Submodule -->
							<details>
								<summary><b>components</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ frontend.src.lib.components</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/Games.svelte'>Games.svelte</a></b></td>
											<td style='padding: 8px;'>- The <code>Games.svelte</code> file in the <code>frontend/src/lib/components</code> directory is a crucial component of the projects user interface, specifically designed to manage and display a list of games<br>- It serves as the primary interface for users to view, filter, and analyze game data<br>- The component interacts with the backend API to fetch game details, synchronize data, and perform analyses<br>- It supports various filtering options such as status, result, time class, and date range, allowing users to customize their view<br>- Additionally, it handles pagination and sorting to efficiently manage large datasets<br>- This component is integral to providing users with a comprehensive and interactive experience in exploring game statistics and insights within the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/SetupWizard.svelte'>SetupWizard.svelte</a></b></td>
											<td style='padding: 8px;'>- The <code>SetupWizard.svelte</code> file is a component within the frontend of the project, designed to guide users through an initial configuration process<br>- Its primary purpose is to facilitate the setup by dynamically assessing system resources and recommending optimal settings for the application<br>- This component enhances user experience by automating the configuration of technical parameters such as CPU threads and memory allocation, ensuring the application runs efficiently on the users system<br>- It also provides mechanisms for users to complete or skip the setup process, integrating seamlessly into the broader application workflow.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/Header.svelte'>Header.svelte</a></b></td>
											<td style='padding: 8px;'>- The Header component in the frontend of the application provides a consistent navigation interface for users<br>- It features a logo and a navigation bar with links to key sections such as Home, Settings, Sync, and Games<br>- Utilizing Sveltes SPA router, it ensures active link highlighting for improved user experience, while maintaining a responsive and visually appealing design across different devices.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/GameView.svelte'>GameView.svelte</a></b></td>
											<td style='padding: 8px;'>- The <code>GameView.svelte</code> file is a key component of the frontend architecture, responsible for rendering and managing the interactive chessboard interface within the application<br>- It leverages the <code>Chessground</code> library to provide a visually engaging and responsive chessboard, while integrating with <code>chess.js</code> to handle the underlying chess logic<br>- Additionally, the component incorporates various classification icons to visually represent the quality of moves, enhancing the user experience by providing immediate feedback on gameplay<br>- This file plays a crucial role in the user interface, offering both functionality and aesthetic appeal to the chess-playing experience.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/Settings.svelte'>Settings.svelte</a></b></td>
											<td style='padding: 8px;'>- Manage user settings and database operations within the frontend of the application<br>- This component facilitates the configuration of Chess.com integration, Stockfish engine parameters, and application appearance<br>- It also provides functionality for loading, updating, and resetting settings, as well as managing the games database through download, upload, and clear operations, ensuring a seamless user experience in personalizing and maintaining the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/Home.svelte'>Home.svelte</a></b></td>
											<td style='padding: 8px;'>- The Home.svelte component serves as the main dashboard interface for the Chess Analyzer application<br>- It provides users with an overview of game statistics and sync status, enabling them to monitor game analysis progress and sync operations<br>- The component also offers quick navigation to key features such as syncing games, configuring settings, and browsing games, enhancing user interaction and engagement with the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/components/Sync.svelte'>Sync.svelte</a></b></td>
											<td style='padding: 8px;'>- Facilitates synchronization of Chess.com games into a local database by providing a user interface for initiating and monitoring the sync process<br>- It allows users to specify a username and time range for the sync, displays real-time status updates, and handles success or error notifications<br>- This component enhances user interaction within the frontend by managing sync operations and displaying relevant feedback.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- api Submodule -->
							<details>
								<summary><b>api</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ frontend.src.lib.api</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/frontend/src/lib/api/client.js'>client.js</a></b></td>
											<td style='padding: 8px;'>- Facilitates communication between the frontend and backend by providing a centralized API client<br>- It manages API requests for settings, system resources, synchronization, games, database management, and game analysis<br>- The client handles error responses, supports environment-specific configurations, and ensures robust error handling to improve user experience and maintain seamless interaction with the backend services.</td>
										</tr>
									</table>
								</blockquote>
							</details>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- backend Submodule -->
	<details>
		<summary><b>backend</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ backend</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Define the backend dependencies required for the project, ensuring a robust and efficient environment for development and deployment<br>- By specifying essential libraries such as FastAPI for building APIs, SQLAlchemy for database interactions, and Uvicorn for ASGI server capabilities, the file supports the projects architecture in handling web requests, database operations, and other functionalities like chess logic and system monitoring.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/Dockerfile'>Dockerfile</a></b></td>
					<td style='padding: 8px;'>- Facilitates the deployment of a Python-based backend application using Docker<br>- Establishes a lightweight environment with Python 3.11, installs necessary dependencies, and sets up the application for execution<br>- Supports seamless integration with the broader architecture by exposing port 42069, allowing the application to be accessed and interact with other components of the system efficiently.</td>
				</tr>
			</table>
			<!-- app Submodule -->
			<details>
				<summary><b>app</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ backend.app</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/main.py'>main.py</a></b></td>
							<td style='padding: 8px;'>- Establishes the core FastAPI application, managing the initialization of database settings and ensuring proper directory permissions<br>- Integrates various API routers for settings, synchronization, games, system resources, and database management<br>- Configures CORS to allow cross-origin requests, facilitating seamless interaction with the frontend<br>- Provides a foundation for handling application lifecycle events and maintaining essential configurations for the backend service.</td>
						</tr>
					</table>
					<!-- crud Submodule -->
					<details>
						<summary><b>crud</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ backend.app.crud</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/crud/games.py'>games.py</a></b></td>
									<td style='padding: 8px;'>- Manage and interact with game data within the database, focusing on CRUD operations and filtering capabilities<br>- Facilitate retrieval of games by various identifiers, creation of new entries, and bulk operations while ensuring duplicates are handled<br>- Support pagination, sorting, and filtering for efficient data access, and enable updates to game analysis statuses, enhancing the overall data management and retrieval process in the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/crud/settings.py'>settings.py</a></b></td>
									<td style='padding: 8px;'>- Manage application settings by providing asynchronous functions to retrieve and update configuration data stored in the database<br>- Facilitate seamless access to all settings as a dictionary and enable updates by merging new values into the existing settings<br>- Enhance the backends ability to dynamically adjust configurations, supporting efficient and flexible application behavior within the broader project architecture.</td>
								</tr>
							</table>
						</blockquote>
					</details>
					<!-- db Submodule -->
					<details>
						<summary><b>db</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ backend.app.db</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/db/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Define the data models for the applications database, focusing on the representation of chess games and application settings<br>- The <code>Game</code> model captures essential details about each chess game, including player information, ratings, and game metadata<br>- The <code>Setting</code> model manages key-value pairs for application configurations<br>- These models form the backbone of the database layer, facilitating data storage and retrieval within the broader application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/db/database.py'>database.py</a></b></td>
									<td style='padding: 8px;'>- Establishes the database connection and session management for the backend of the application<br>- Utilizes SQLAlchemys asynchronous capabilities to interact with a SQLite database, ensuring efficient and non-blocking database operations<br>- Provides a session generator function to facilitate database interactions throughout the application, promoting a consistent and streamlined approach to handling database sessions within the projects architecture.</td>
								</tr>
							</table>
						</blockquote>
					</details>
					<!-- api Submodule -->
					<details>
						<summary><b>api</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ backend.app.api</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/api/sync.py'>sync.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates the synchronization of chess games from Chess.com into the applications database<br>- It provides an API endpoint to initiate the sync process, which runs as a background task to prevent blocking<br>- The sync operation retrieves game data using a specified username and optional time limit, updates the database, and offers an endpoint to check the current sync status and results.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/api/database.py'>database.py</a></b></td>
									<td style='padding: 8px;'>- Manage the database lifecycle for the backend of the application, providing endpoints to initialize, clear, download, and upload the database<br>- This functionality ensures the database is correctly set up, maintained, and backed up, while also allowing users to replace or retrieve the database file as needed<br>- It supports maintaining data integrity and operational continuity within the applications architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/api/games.py'>games.py</a></b></td>
									<td style='padding: 8px;'>- Manage and analyze chess games within the backend architecture by providing endpoints for retrieving, analyzing, and obtaining statistics about games<br>- It supports filtering, sorting, and pagination of game data, and integrates with the Stockfish engine for game analysis<br>- The module ensures efficient handling of game data and analysis results, facilitating robust interaction with the chess game database.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/api/settings.py'>settings.py</a></b></td>
									<td style='padding: 8px;'>- Manage application settings through a RESTful API endpoint, facilitating retrieval and updates<br>- Utilize FastAPI to define routes for reading and writing settings, leveraging asynchronous database sessions for efficient data handling<br>- Ensure data integrity by validating settings before updates, and handle potential errors with appropriate HTTP responses<br>- This component integrates with the broader system to maintain consistent configuration management across the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/api/system_resources.py'>system_resources.py</a></b></td>
									<td style='padding: 8px;'>- Provide an API endpoint to retrieve system resource information, including CPU, memory, and Stockfish status, within the backend architecture<br>- Utilize FastAPI and SQLAlchemy to handle asynchronous database sessions and fetch settings<br>- Integrate system resource data with Stockfish validation, ensuring accurate and comprehensive resource monitoring for the application<br>- This enhances the systems capability to manage and optimize resource utilization effectively.</td>
								</tr>
							</table>
						</blockquote>
					</details>
					<!-- services Submodule -->
					<details>
						<summary><b>services</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ backend.app.services</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/services/stockfish_service.py'>stockfish_service.py</a></b></td>
									<td style='padding: 8px;'>- The <code>stockfish_service.py</code> file is an integral component of the backend services in this project, primarily responsible for interfacing with the Stockfish chess engine<br>- Its main purpose is to retrieve configuration settings for Stockfish from the database, ensuring that the engine operates with the correct parameters such as path, thread count, hash size, analysis depth, and analysis time<br>- By fetching and merging these settings with predefined defaults, the service ensures that Stockfish is configured optimally for chess analysis tasks<br>- This functionality is crucial for maintaining the adaptability and efficiency of the chess engine within the broader application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/services/chess_com.py'>chess_com.py</a></b></td>
									<td style='padding: 8px;'>- The <code>chess_com.py</code> service facilitates interaction with the Chess.com public API, enabling retrieval of a users game archives and extraction of detailed game data<br>- It supports fetching games from specific monthly archives or across multiple months, providing structured information such as player details, game results, and ratings<br>- This service is integral to analyzing and processing chess game data within the broader application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/backend/app/services/system_resources.py'>system_resources.py</a></b></td>
									<td style='padding: 8px;'>- Provide system resource information and validate settings for the Stockfish chess engine<br>- It gathers CPU and memory details, checks the validity of the Stockfish binary path, and ensures that user-defined settings like threads, hash size, and analysis parameters are compatible with available resources<br>- This functionality supports efficient resource management and optimal performance within the broader application architecture.</td>
								</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- scripts Submodule -->
	<details>
		<summary><b>scripts</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ scripts</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/scripts/run-images.ps1'>run-images.ps1</a></b></td>
					<td style='padding: 8px;'>- Facilitates the execution of Docker images by ensuring Docker is installed and running on the system<br>- It sets default values for image owner and tag, and attempts to run a corresponding Bash script using either Git Bash or WSL if available<br>- This script is integral for automating Docker image operations within the projects development environment, enhancing cross-platform compatibility and user convenience.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/scripts/dev.sh'>dev.sh</a></b></td>
					<td style='padding: 8px;'>- The <code>scripts/dev.sh</code> script facilitates the local development environment setup for the Local Chess Analyzer project<br>- It orchestrates the startup of both backend and frontend services using Docker Compose, ensuring that the necessary directories are created and the services are accessible via specified local URLs<br>- Additionally, it manages the cleanup of Docker containers upon termination, streamlining the development workflow.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/scripts/run-images.sh'>run-images.sh</a></b></td>
					<td style='padding: 8px;'>- The <code>scripts/run-images.sh</code> file is a crucial component of the project, designed to manage the execution of Docker images for both the backend and frontend services of the application<br>- Its primary purpose is to ensure that these services are run with robust checks and clear error handling, facilitating a smooth deployment process<br>- The script is configurable via environment variables, allowing flexibility in specifying image versions, port settings, and health check parameters<br>- By automating the handling of port conflicts and setting health check timeouts, it enhances the reliability and efficiency of deploying the applications Dockerized components<br>- This script is integral to the projects architecture, as it streamlines the process of running and managing the application's containerized environments.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/.github/workflows/release.yml'>release.yml</a></b></td>
							<td style='padding: 8px;'>- Automate the release process by creating platform-specific bundles for macOS and Windows upon tagging a new version<br>- The workflow prepares executable scripts and instructions for both operating systems, ensuring compatibility with Docker Desktop<br>- It generates checksums for integrity verification and publishes the bundles as a GitHub release, facilitating easy access and deployment for users.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/.github/workflows/release-images.yml'>release-images.yml</a></b></td>
							<td style='padding: 8px;'>- Automates the release of Docker images for the Local Chess Analyzer project by triggering on new version tags<br>- It builds and pushes backend and frontend images to the GitHub Container Registry, generates a Docker Compose file for deployment, and creates a GitHub release with the necessary artifacts and instructions for quick deployment, ensuring streamlined and consistent image distribution.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/tarekchaalan/local-chess-analyzer/blob/master/.github/workflows/push-images.yml'>push-images.yml</a></b></td>
							<td style='padding: 8px;'>- Automate the process of building and pushing Docker images for both the backend and frontend components of the project to the GitHub Container Registry upon every push to any branch<br>- It ensures that images are tagged with both branch and commit-specific identifiers, and updates the latest tag when changes are pushed to the main branch, facilitating continuous integration and deployment.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following:

- **Languages:** Python 3.11+, JavaScript (Node.js 20+)
- **Package Managers:** npm, pip
- **Container Runtime:** Docker and Docker Compose

### Installation

Build local-chess-analyzer from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/tarekchaalan/local-chess-analyzer
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd local-chess-analyzer
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![docker][docker-shield]][docker-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [docker-shield]: https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white -->
	<!-- [docker-link]: https://www.docker.com/ -->

	**Using [docker](https://www.docker.com/):**

	```sh
	❯ docker compose -f docker-compose.yml build
	```
<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![npm][npm-shield]][npm-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [npm-shield]: None -->
	<!-- [npm-link]: None -->

	**Using npm (frontend dependencies):**

	```sh
	❯ cd frontend
	❯ npm install
	```
<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![pip][pip-shield]][pip-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [pip-shield]: None -->
	<!-- [pip-link]: None -->

	**Using pip (backend dependencies):**

	```sh
	❯ cd backend
	❯ python3 -m venv .venv
	❯ source .venv/bin/activate
	❯ pip install -r requirements.txt
	```

### Usage

Run the project with:

**Using [docker](https://www.docker.com/):**
```sh
docker compose -f docker-compose.yml up --build
```
- Frontend: http://localhost:6969
- Backend API: http://localhost:42069
- API Docs: http://localhost:42069/docs

**Using npm (frontend dev) + pip (backend dev):**
- Terminal 1 (backend):
```sh
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 42069
```
- Terminal 2 (frontend):
```sh
cd frontend
VITE_API_BASE_URL=http://localhost:42069 npm run dev
```

### Testing

Automated tests are not configured yet in this repository.
- Backend suggestion: add Pytest and run with `pytest`.
- Frontend suggestion: add Vitest and run with `npm run test`.

---

## Roadmap

- [ ] Stockfish analysis worker: background processor for queued games
- [ ] Frontend: settings UI, game list, interactive board, analysis views
- [ ] Sync controls: trigger sync and display status in UI
- [ ] Advanced: openings analysis, mistake patterns, performance trends, engine comparisons

---

## Contributing

- **🐛 [Report Issues](https://github.com/tarekchaalan/local-chess-analyzer/issues)**: Submit bugs found or log feature requests for the `local-chess-analyzer` project.
- **💡 [Submit Pull Requests](https://github.com/tarekchaalan/local-chess-analyzer/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/tarekchaalan/local-chess-analyzer
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/tarekchaalan/local-chess-analyzer/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=tarekchaalan/local-chess-analyzer">
   </a>
</p>
</details>

---

## License

This project includes Stockfish, which is licensed under the GNU General Public License v3.0. See [LICENSE](./LICENSE) for details.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

---

<p>this README was made by an AI tool - pretty cool imo</p>

---
