# Lumin
Lumin is a Discord bot project with the purpose of updating & refactoring it's predecessor, FightMan01 bot. It's a multi-purpose bot, with features such as moderation, fun, and utility commands.

## Running the bot
### Prerequisites
- Python 3.12 or above
- PostgreSQL
- It is recommended to use MacOS or Linux for running the bot because of **uvloop**
### Steps
1. Clone the repository
2. Install the required packages using `pip install --upgrade -r requirements.txt`
    - You can use virtual environments to keep the dependencies isolated from your system _(recommended)_
3. Create a `.env` file in the root directory of the project, this needs to have 4 keys:
    - `TOKEN`, containing your bot's token
    - `DB_HOST`, containing the IP address for your database (can be _`localhost`_ as well)
    - `DB_PASSWORD`, containing the password for your database
    - `DB_PORT`, containing the port for your database
4. Install PostgreSQL
    - Create a user called `lumin` with the password you set in the `.env` file
    - Create a database called `lumin` (preferably with the owner being the `lumin` user, for security purposes)
    - If you want to 100% make sure tables are created, copy and paste the contents of `first_time.sql`
5. Run the bot using `python main.py`

## Contributor notice
1. We are using ClickUp to assign tasks to our developers. Outsiders will never have access to this, but you are free to
improve on our code - send a PR and we will consider it! :3
2. We are using a subclassed `commands.Context`, you can find the code in `main.py`. Import using `import main` and
refer to it using `main.Context`. This is for easier localization workflow. Read the docstring for more information.
3. The default language is English. When adding new commands and features, you are only required to add localized
messages in English.
4. We use `discord-localization`, a custom-made package, for localization purposes. You can read more
[here](https://pypi.org/project/discord-localization).
5. We use NumPy-style docstrings. You should add docstrings to every function that isn't a command, unless the name of
the function represents its purpose (such as `load_cogs`).
6. Helpers are used for commonly used features that aren't module-specific (e.x. `EconomyHelper` in `economy.py`).
7. For formatting purposes, we use custom arguments that can be created from the objects they represent. For example,
`CustomUser` can be created from a `discord.User` using `CustomUser.from_user(<discord.User>)`. We need this so that
custom messages edited by server admins can't access sensitive information, but also for ease-of-use (e.x `User.avatar`
returns a `discord.Asset`, so `CustomUser.avatar` already returns that asset's URL, because that is most likely what
server admins expect to see.)
8. If you have any questions, DM **@pearoo** on Discord.

## Versioning & releasing
Given a version number MAJOR.MINOR.PATCH:
- MAJOR is updated when we introduce a breaking change (such as reworking an entire module)
  - When MAJOR is updated, MINOR and PATCH are reset to 0
- MINOR is updated when we update only a small set of commands
  - When MINOR is updated, PATCH is reset to 0
- PATCH is updated for hotfixes, BTS optimization changes, and localization updates
- Additional labels included after the version numbers are not going to be present on the live bot
