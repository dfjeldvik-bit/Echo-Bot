import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta, timezone
import random
import asyncio

LOG_FILE = "mod_logs.json"
WARNS_FILE = "warns.json"
INFRACTIONS_FILE = "infractions.json"
VERIFY_FILE = "verification.json"
VERIFIED_ROLE_FILE = "verified_roles.json"
ERROR_FILE = "error_channels.json"
BOTDM_FILE = "botdm.json"
BOT_COMMANDS_FILE = "bot_commands.json"
ECONOMY_FILE = "economy.json"
ECONOMY_CHANNELS_FILE = "economy_channels.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

mod_log_channels = load_json(LOG_FILE, {})
warns_data = load_json(WARNS_FILE, {})
infractions = load_json(INFRACTIONS_FILE, {})
verify_channels = load_json(VERIFY_FILE, {})
verified_roles = load_json(VERIFIED_ROLE_FILE, {})
error_channels = load_json(ERROR_FILE, {})
botdm_channels = load_json(BOTDM_FILE, {})
bot_commands_channels = load_json(BOT_COMMANDS_FILE, {})
economy_data = load_json(ECONOMY_FILE, {})
economy_channels = load_json(ECONOMY_CHANNELS_FILE, {})

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

utc = timezone.utc

ATTACKER_ID = 428862995391451156
PROTECTED_ID = 1401255591749488781

def is_protected_action(ctx, member):
    if ctx.author.id == ATTACKER_ID and member.id == PROTECTED_ID:
        return True
    return False

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} • {bot.user.id}")
    print("All commands should work now → try !ping, !kick @user, etc.")
    print("─" * 50)

@bot.event
async def on_disconnect():
    pass

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.reply(f"Pong! Latency: {latency} ms.")

@bot.command()
async def hello(ctx):
    await ctx.reply("Hello. We hope you enjoy your time in the server.")

async def paginate(ctx, embeds):
    if not embeds:
        return
    current = 0
    if len(embeds) == 1:
        await ctx.reply(embed=embeds[0])
        return
    class PaginationView(discord.ui.View):
        def __init__(self, author, embeds, current):
            super().__init__(timeout=60)
            self.author = author
            self.embeds = embeds
            self.current = current
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user == self.author
        @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current = (self.current - 1) % len(self.embeds)
            await interaction.response.edit_message(embed=self.embeds[self.current])
        @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current = (self.current + 1) % len(self.embeds)
            await interaction.response.edit_message(embed=self.embeds[self.current])
    view = PaginationView(ctx.author, embeds, current)
    await ctx.reply(embed=embeds[0], view=view)

@bot.command(name="commands", aliases=["cmnds"])
async def simple_help(ctx):
    lines = [
        "**Moderation:**",
        "`!kick @user|u [reason]`",
        "`!ban @user|ID|u [reason]`",
        "`!unban @user|ID|u [reason]`",
        "`!t @user|u <duration> [reason]` (e.g., 1h, 1m, 1h)",
        "`!untime @user|ID|u [reason]`",
        "`!warn @user|u [reason]`",
        "`!warns @user|u`",
        "`!clearwarns @user|u`",
        "`!remove-inf @user|u <num>`",
        "`!inf @user|u`",
        "`!purge <limit>`",
        "`!purge all`",
        "`!d` (reply to a message)",
        "`!dm @user|u <message>` (admin only)",
        "`!say #channel <message>` (admin only)",
        "`!lock`",
        "`!unlock`",
        "`!dc @user|u` (disconnect from VC)",
        "`!m @user|u` (move to your VC)",
        "",
        "**Fun & Utility:**",
        "`!hello`",
        "`!bam @user|u [reason]` (fake ban for verified users)",
        "`!unbam @user|u [reason]` (reverse fake ban for verified users)",
        "`!breake @user|u [reason]` (fake timeout for verified users)",
        "`!set-voice-status <message>` (in VC)",
        "`!members`",
        "`!onlinewhere`",
        "`!myroles`",
        "`!roles`",
        "",
        "**Economy System:**",
        "`!work`",
        "`!coins [@user|u|ID]`",
        "`!bal [@user|u|ID]`",
        "`!balance [@user|u|ID]`",
        "`!rob @user|u`",
        "`!beg`",
        "`!gamble <amount>`",
        "`!deposit <amount>`",
        "`!withdraw <amount>`",
        "`!shop`",
        "`!buy <item>`",
        "`!inventory`",
        "`!use <item>`",
        "`!using`",
        "`!start-business <name>`",
        "`!business`",
        "`!business-deposit <amount>`",
        "`!stock`",
        "`!restocking <amount>`",
        "`!upgrades`",
        "`!upgrade <upgrade>`",
        "`!set-wage @user <percent>`",
        "`!wage`",
        "`!wages <business>`",
        "`!hire-employee @user`",
        "`!fire @user`",
        "`!business-leave`",
        "`!hire-manager @user`",
        "`!cd`",
        "`!gift @user <amount>`",
        "`!give-coins @user <amount>`",
        "",
        "**Admin Commands:**",
        "`!setinf @user|ID|u <type> <num> [reason]`",
        "`!info`",
        "`!slowmode <seconds>`",
        "`!nick @user|u <new_nick>`",
        "`!remove-nickname @user|u`",
        "`!forceverify @user|u|ID`",
        "",
        "**Setup:**",
        "`!setmodlog #channel`",
        "`!setboterrors #channel`",
        "`!setbotdm #channel`",
        "`!setverifychannel #channel`",
        "`!setverifyrole @role`",
        "`!setbotcommands #channel`",
        "`!seteconomy #channel`",
        "`!verify`",
        "",
        "**Other:**",
        "`!help`",
        "`!ping`",
    ]
    per_page = 20
    pages = [lines[i:i + per_page] for i in range(0, len(lines), per_page)]
    embeds = []
    for idx, page in enumerate(pages, 1):
        embed = discord.Embed(title=f"Help Menu - Page {idx}/{len(pages)}", description="\n".join(page), color=discord.Color.blue())
        embeds.append(embed)
    await paginate(ctx, embeds)

@bot.command()
async def help(ctx):
    embed = discord.Embed(description="get lvl 15 and be active to get official Member role", color=discord.Color.blue())
    await ctx.reply(embed=embed)

async def send_log_embed(guild, embed):
    gid = str(guild.id)
    if gid not in mod_log_channels:
        return
    ch = bot.get_channel(mod_log_channels[gid])
    if ch:
        try:
            await ch.send(embed=embed)
        except:
            pass

async def send_error_embed(guild, embed):
    gid = str(guild.id)
    if gid not in error_channels:
        return
    ch = bot.get_channel(error_channels[gid])
    if ch:
        try:
            await ch.send(embed=embed)
        except:
            pass

async def log_action(ctx, action: str, target, reason=None, extra=None):
    color = discord.Color.red() if "Ban" in action else \
            discord.Color.orange() if any(x in action for x in ["Kick", "Timeout", "Warn"]) else \
            discord.Color.green()
    embed = discord.Embed(title=f"{action}", color=color, timestamp=datetime.now(utc))
    embed.add_field(name="User", value=f"{target} ({target.id})", inline=True)
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
    embed.add_field(name="Reason", value=reason or "None", inline=False)
    if extra:
        embed.add_field(name="Extra", value=extra, inline=False)
    embed.set_footer(text=ctx.guild.name)
    await send_log_embed(ctx.guild, embed)

def add_infraction(guild_id: str, user_id: str, action_type: str, reason: str, mod_id: str):
    if guild_id not in infractions:
        infractions[guild_id] = {}
    if user_id not in infractions[guild_id]:
        infractions[guild_id][user_id] = []
    infractions[guild_id][user_id].append({
        "type": action_type,
        "reason": reason or "None",
        "mod": mod_id,
        "time": datetime.now(utc).isoformat()
    })
    save_json(INFRACTIONS_FILE, infractions)

def remove_infractions(guild_id: str, user_id: str, num: int):
    if guild_id not in infractions or user_id not in infractions[guild_id] or len(infractions[guild_id][user_id]) < num:
        return False
    removed = infractions[guild_id][user_id][-num:]
    infractions[guild_id][user_id] = infractions[guild_id][user_id][:-num]
    save_json(INFRACTIONS_FILE, infractions)
    if guild_id in warns_data and user_id in warns_data[guild_id]:
        for _ in range(num):
            if len(warns_data[guild_id][user_id]) > 0:
                warns_data[guild_id][user_id].pop()
        save_json(WARNS_FILE, warns_data)
    return True

def clear_warns(guild_id: str, user_id: str):
    if guild_id not in warns_data or user_id not in warns_data[guild_id]:
        return 0
    num_warns = len(warns_data[guild_id][user_id])
    warns_data[guild_id][user_id] = []
    save_json(WARNS_FILE, warns_data)
    if guild_id in infractions and user_id in infractions[guild_id]:
        infractions[guild_id][user_id] = [inf for inf in infractions[guild_id][user_id] if inf['type'] != 'Warn']
        save_json(INFRACTIONS_FILE, infractions)
    return num_warns

async def has_verified_role(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    gid = str(ctx.guild.id)
    if gid not in verified_roles:
        return False
    verified_role = ctx.guild.get_role(verified_roles[gid])
    if not verified_role:
        return False
    return verified_role in member.roles

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodlog(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!setmodlog #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    mod_log_channels[str(ctx.guild.id)] = channel.id
    save_json(LOG_FILE, mod_log_channels)
    embed = discord.Embed(description=f"Mod logs set to {channel.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setboterrors(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!setboterrors #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    error_channels[str(ctx.guild.id)] = channel.id
    save_json(ERROR_FILE, error_channels)
    embed = discord.Embed(description=f"Bot errors set to {channel.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setbotdm(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!setbotdm #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    botdm_channels[str(ctx.guild.id)] = channel.id
    save_json(BOTDM_FILE, botdm_channels)
    embed = discord.Embed(description=f"Bot DM logs set to {channel.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setbotcommands(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!setbotcommands #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    bot_commands_channels[str(ctx.guild.id)] = channel.id
    save_json(BOT_COMMANDS_FILE, bot_commands_channels)
    embed = discord.Embed(description=f"Bot commands channel set to {channel.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def seteconomy(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!seteconomy #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    economy_channels[gid] = channel.id
    save_json(ECONOMY_CHANNELS_FILE, economy_channels)
    embed = discord.Embed(description=f"Economy commands channel set to {channel.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

async def get_member_or_id(ctx, target):
    if isinstance(target, discord.Member):
        return target
    if isinstance(target, str):
        if target.isdigit():
            try:
                member = await ctx.guild.fetch_member(int(target))
                return member
            except:
                return None
        else:
            try:
                converter = commands.MemberConverter()
                member = await converter.convert(ctx, target)
                return member
            except:
                return None
    return None

async def get_target(ctx, target):
    if isinstance(target, str) and target.lower() == "u" and ctx.message.reference:
        try:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            return ref_msg.author
        except:
            pass
    return target

def parse_duration(dur: str) -> timedelta:
    dur = dur.lower().strip()
    if dur.endswith('d'):
        num = int(dur[:-1])
        return timedelta(days=num)
    elif dur.endswith('h'):
        num = int(dur[:-1])
        return timedelta(hours=num)
    elif dur.endswith('m'):
        num = int(dur[:-1])
        return timedelta(minutes=num)
    else:
        raise ValueError("Invalid unit. Use m, h, d.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member == ctx.author:
        embed = discord.Embed(description="u cannot preform this acction on yourself", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(description="You cannot moderate a user with an equal or higher role than you.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.me.top_role:
        embed = discord.Embed(description="Cannot kick this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="User Kicked", description=f"{member.mention} has been kicked.", color=discord.Color.orange())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.reply(embed=embed)
        await log_action(ctx, "Kicked", member, reason)
        add_infraction(str(ctx.guild.id), str(member.id), "Kick", reason, str(ctx.author.id))
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member == ctx.author:
        embed = discord.Embed(description="u cannot preform this acction on yourself", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(description="You cannot moderate a user with an equal or higher role than you.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.me.top_role:
        embed = discord.Embed(description="Cannot ban this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.ban(reason=reason, delete_message_days=0)
        embed = discord.Embed(title="User Banned", description=f"{member.mention} has been banned.", color=discord.Color.red())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.reply(embed=embed)
        await log_action(ctx, "Banned", member, reason)
        add_infraction(str(ctx.guild.id), str(member.id), "Ban", reason, str(ctx.author.id))
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    if isinstance(target, str) and target.isdigit():
        try:
            target = await bot.fetch_user(int(target))
        except:
            embed = discord.Embed(description="Invalid user ID.", color=discord.Color.red())
            return await ctx.reply(embed=embed)
    elif isinstance(target, str):
        try:
            converter = commands.UserConverter()
            target = await converter.convert(ctx, target)
        except:
            embed = discord.Embed(description="Invalid user.", color=discord.Color.red())
            return await ctx.reply(embed=embed)
    try:
        await ctx.guild.unban(target, reason=reason)
        embed = discord.Embed(title="User Unbanned", description=f"{target.mention} has been unbanned.", color=discord.Color.green())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.reply(embed=embed)
        await log_action(ctx, "Unbanned", target, reason)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def t(ctx, target, duration: str, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member == ctx.author:
        embed = discord.Embed(description="u cannot preform this acction on yourself", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(description="You cannot moderate a user with an equal or higher role than you.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.me.top_role:
        embed = discord.Embed(description="Cannot timeout this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        delta = parse_duration(duration)
        if delta > timedelta(days=28):
            embed = discord.Embed(description="Timeout cannot exceed 28 days.", color=discord.Color.red())
            return await ctx.reply(embed=embed)
        until = datetime.now(utc) + delta
        await member.timeout(until, reason=reason)
        embed = discord.Embed(title="User Timed Out", description=f"{member.mention} has been timed out for {duration}.", color=discord.Color.orange())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.reply(embed=embed)
        await log_action(ctx, "Timeout", member, reason, f"Duration: {duration}")
        add_infraction(str(ctx.guild.id), str(member.id), f"Timeout ({duration})", reason, str(ctx.author.id))
    except ValueError:
        embed = discord.Embed(description="Invalid duration. Use formats such as 1h, 4m, 5d.", color=discord.Color.red())
        await ctx.reply(embed=embed)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def untime(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.timeout(None, reason=reason)
        embed = discord.Embed(title="Timeout Removed", description=f"{member.mention}'s timeout has been removed.", color=discord.Color.green())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.reply(embed=embed)
        await log_action(ctx, "Untimeout", member, reason)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member == ctx.author:
        embed = discord.Embed(description="u cannot preform this acction on yourself", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.author.top_role:
        embed = discord.Embed(description="You cannot moderate a user with an equal or higher role than you.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.top_role >= ctx.me.top_role or member.bot:
        embed = discord.Embed(description="Cannot warn this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    if gid not in warns_data:
        warns_data[gid] = {}
    if uid not in warns_data[gid]:
        warns_data[gid][uid] = []
    warns_data[gid][uid].append({
        "reason": reason or "None",
        "mod": str(ctx.author.id),
        "time": datetime.now(utc).isoformat()
    })
    save_json(WARNS_FILE, warns_data)
    count = len(warns_data[gid][uid])
    embed = discord.Embed(title="User Warned", description=f"{member.mention} has been warned ({count}/3).", color=discord.Color.orange())
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.reply(embed=embed)
    await log_action(ctx, "Warned", member, reason, f"Total: {count}")
    add_infraction(gid, uid, "Warn", reason, str(ctx.author.id))
    try:
        await member.send(f"You have been warned in {ctx.guild.name}: {reason or 'None'} (#{count})")
    except:
        pass

@bot.command(name="warns")
@commands.has_permissions(administrator=True)
async def warns(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    warns = warns_data.get(gid, {}).get(uid, [])
    if not warns:
        embed = discord.Embed(description=f"{member.mention} has no warnings.", color=discord.Color.blue())
        return await ctx.reply(embed=embed)
    warns = warns[::-1]
    per_page = 5
    chunks = [warns[i:i + per_page] for i in range(0, len(warns), per_page)]
    embeds = []
    for page_num, chunk in enumerate(chunks, 1):
        embed = discord.Embed(title=f"Warnings for {member} ({len(warns)} total) - Page {page_num}/{len(chunks)}", color=discord.Color.orange())
        for i, warn in enumerate(chunk, (page_num - 1) * per_page + 1):
            embed.add_field(name=f"#{i} {warn['time'][:10]}", value=f"Reason: {warn['reason']}\nBy: <@{warn['mod']}>", inline=False)
        embeds.append(embed)
    await paginate(ctx, embeds)
    await log_action(ctx, "Checked Warnings", member, reason=None, extra=f"Count: {len(warns)}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    num_cleared = clear_warns(gid, uid)
    if num_cleared > 0:
        embed = discord.Embed(title="Warnings Cleared", description=f"Cleared {num_cleared} warning(s) for {member.mention}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        await log_action(ctx, "Cleared Warnings", member, reason="Manual clear", extra=f"Cleared {num_cleared} warnings")
    else:
        embed = discord.Embed(description=f"{member.mention} has no warnings to clear.", color=discord.Color.blue())
        await ctx.reply(embed=embed)

@bot.command(name="remove-inf")
@commands.has_permissions(administrator=True)
async def remove_inf(ctx, target, num: int):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if num < 1:
        embed = discord.Embed(description="Number must be at least 1.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    if remove_infractions(gid, uid, num):
        embed = discord.Embed(title="Infractions Removed", description=f"Removed {num} infraction(s) from {member.mention}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        await log_action(ctx, f"Removed {num} Infractions", member, reason="Manual removal")
    else:
        embed = discord.Embed(description=f"{member.mention} does not have enough infractions.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def inf(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    if gid not in infractions or uid not in infractions[gid]:
        embed = discord.Embed(description=f"{member} has no infractions.", color=discord.Color.blue())
        return await ctx.reply(embed=embed)
    recs = infractions[gid][uid][::-1]
    per_page = 5
    chunks = [recs[i:i + per_page] for i in range(0, len(recs), per_page)]
    embeds = []
    for page_num, chunk in enumerate(chunks, 1):
        embed = discord.Embed(title=f"Infractions for {member} ({len(recs)} total) - Page {page_num}/{len(chunks)}", color=discord.Color.red())
        for i, rec in enumerate(chunk, (page_num - 1) * per_page + 1):
            embed.add_field(name=f"#{i} {rec['time'][:10]} - {rec['type']}", value=f"Reason: {rec['reason']}\nBy: <@{rec['mod']}>", inline=False)
        embeds.append(embed)
    await paginate(ctx, embeds)

@bot.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, *args):
    if len(args) == 0:
        embed = discord.Embed(description="Usage: `!purge <limit>` or `!purge all`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if args[0].lower() == "all":
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(description="You must be an admin to use `!purge all`.", color=discord.Color.red())
            return await ctx.reply(embed=embed)
        embed = discord.Embed(title="Confirm Purge All", description="Are you sure you want to purge all messages in this channel? This action cannot be undone.", color=discord.Color.red())
        class ConfirmView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=30)
                self.author = author
                self.confirmed = False
            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user == self.author
            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.confirmed = True
                await interaction.response.edit_message(content="Purging...", embed=None, view=None)
                self.stop()
        view = ConfirmView(ctx.author)
        msg = await ctx.reply(embed=embed, view=view)
        await view.wait()
        if not view.confirmed:
            await msg.edit(content="Purge cancelled.", embed=None, view=None)
            return
        deleted = 0
        while True:
            msgs = [m async for m in ctx.channel.history(limit=100)]
            if not msgs:
                break
            await ctx.channel.delete_messages(msgs)
            deleted += len(msgs)
            if len(msgs) < 100:
                break
        embed = discord.Embed(title="Purge Complete", description=f"Deleted {deleted} messages.", color=discord.Color.dark_grey())
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=5)
    else:
        try:
            limit = int(args[0])
            if limit < 1:
                embed = discord.Embed(description="Limit must be at least 1.", color=discord.Color.red())
                return await ctx.reply(embed=embed)
            deleted = await ctx.channel.purge(limit=limit, before=ctx.message)
            embed = discord.Embed(title="Purge Complete", description=f"Deleted {len(deleted)} messages.", color=discord.Color.dark_grey())
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=5)
        except ValueError:
            embed = discord.Embed(description="Invalid limit.", color=discord.Color.red())
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
            await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def d(ctx):
    if not ctx.message.reference:
        embed = discord.Embed(description="Please reply to a message first.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if ctx.author.id == ATTACKER_ID and ref_msg.author.id == PROTECTED_ID:
            embed = discord.Embed(description="You are not allowed to delete this user's messages.", color=discord.Color.red())
            return await ctx.reply(embed=embed)
        await ref_msg.delete()
        await ctx.message.delete()
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    overwrite = discord.PermissionOverwrite(send_messages=False)
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = discord.Embed(description="Channel locked.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    overwrite = discord.PermissionOverwrite(send_messages=None)
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed = discord.Embed(description="Channel unlocked.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def dc(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed = discord.Embed(description="You must be in a voice channel to perform this action.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if not member.voice:
        embed = discord.Embed(description=f"{member.mention} is not in a voice channel.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if ctx.author.voice.channel != member.voice.channel:
        embed = discord.Embed(description="You must be in the same voice channel as the target to perform this action.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.move_to(None)
        embed = discord.Embed(description=f"{member.mention} has been disconnected from the voice channel.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        await log_action(ctx, "Disconnected from VC", member)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def m(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed = discord.Embed(description="You must be in a voice channel to move someone.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if not member.voice:
        embed = discord.Embed(description=f"{member.mention} is not in a voice channel.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if ctx.author.voice.channel != member.voice.channel:
        embed = discord.Embed(description="You must be in the same voice channel as the target to perform this action.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.move_to(ctx.author.voice.channel)
        embed = discord.Embed(description=f"{member.mention} has been moved to your voice channel.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        await log_action(ctx, "Moved to VC", member)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, target, *, message: str):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    try:
        await member.send(message)
        embed = discord.Embed(title="DM Sent", description=f"DM sent to {member.mention}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        gid = str(ctx.guild.id)
        if gid in botdm_channels:
            ch = bot.get_channel(botdm_channels[gid])
            if ch:
                log_embed = discord.Embed(title="DM Logged", description=f"Message: {message}", color=discord.Color.blue(), timestamp=datetime.now(utc))
                log_embed.add_field(name="Sent to", value=member.mention, inline=True)
                log_embed.add_field(name="By", value=ctx.author.mention, inline=True)
                await ch.send(embed=log_embed)
    except Exception as e:
        embed = discord.Embed(description=f"Error sending DM: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, channel: discord.TextChannel, *, message: str):
    try:
        await channel.send(message)
        embed = discord.Embed(title="Message Sent", description=f"Message sent in {channel.mention}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
        await ctx.message.delete()
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setinf(ctx, target, inf_type: str, num: int, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if inf_type.lower() not in ["warn", "timeout"]:
        embed = discord.Embed(description="Invalid type. Use warn or timeout.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    action_type = "Warn" if inf_type.lower() == "warn" else "Timeout"
    for _ in range(num):
        add_infraction(gid, uid, action_type, reason, str(ctx.author.id))
        if inf_type.lower() == "warn":
            if gid not in warns_data:
                warns_data[gid] = {}
            if uid not in warns_data[gid]:
                warns_data[gid][uid] = []
            warns_data[gid][uid].append({
                "reason": reason or "None",
                "mod": str(ctx.author.id),
                "time": datetime.now(utc).isoformat()
            })
            save_json(WARNS_FILE, warns_data)
    embed = discord.Embed(title="Infractions Set", description=f"Added {num} {action_type}(s) to {member.mention}.", color=discord.Color.orange())
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.reply(embed=embed)
    await log_action(ctx, f"Set {num} {action_type}s", member, reason)

@bot.command()
async def bam(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    if gid not in verified_roles:
        embed = discord.Embed(description="No verified role has been set.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    verified_role = ctx.guild.get_role(verified_roles[gid])
    if not verified_role or verified_role not in member.roles:
        embed = discord.Embed(description="This user is not verified. Only verified users can be affected.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    custom_reason = reason or "bitch lol"
    embed = discord.Embed(title="User Banned", description=f"{member.mention} was banned for {custom_reason}.", color=discord.Color.red())
    await ctx.reply(embed=embed)

@bot.command()
async def unbam(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    if gid not in verified_roles:
        embed = discord.Embed(description="No verified role has been set.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    verified_role = ctx.guild.get_role(verified_roles[gid])
    if not verified_role or verified_role not in member.roles:
        embed = discord.Embed(description="This user is not verified. Only verified users can be affected.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    custom_reason = reason or "bitch lol"
    embed = discord.Embed(title="User Unbanned", description=f"{member.mention} has been unbanned. Reason: {custom_reason}", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
async def breake(ctx, target, *, reason: str = None):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    if gid not in verified_roles:
        embed = discord.Embed(description="No verified role has been set.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    verified_role = ctx.guild.get_role(verified_roles[gid])
    if not verified_role or verified_role not in member.roles:
        embed = discord.Embed(description="This user is not verified. Only verified users can be affected.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    custom_reason = reason or "bitch lol"
    embed = discord.Embed(title="User Timed Out", description=f"{member.mention} has been timed out for {custom_reason}.", color=discord.Color.orange())
    await ctx.reply(embed=embed)

@bot.command(name="set-voice-status")
async def set_voice_status(ctx, *, status: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed = discord.Embed(description="You must be in a voice channel to set the status.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    vc = ctx.author.voice.channel
    try:
        await vc.edit(status=status)
        embed = discord.Embed(description=f"Voice channel status set to: {status}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setverifychannel(ctx, channel: discord.TextChannel = None):
    if not channel:
        embed = discord.Embed(description="Usage: `!setverifychannel #channel`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    verify_channels[gid] = channel.id
    save_json(VERIFY_FILE, verify_channels)
    embed = discord.Embed(title="Verify Here", description="Verify to use all the commands and features in the server! React with 👋 to get started. This will give you the verified role allowing you to access fun commands, set birthdays, timezones, and more yk!", color=discord.Color.blue())
    try:
        msg = await channel.send(embed=embed)
        await msg.add_reaction("👋")
        embed = discord.Embed(description=f"Posted in {channel.mention}.", color=discord.Color.green())
        await ctx.reply(embed=embed)
    except Exception as e:
        embed = discord.Embed(description=f"Error: {e}", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setverifyrole(ctx, role: discord.Role = None):
    if not role:
        embed = discord.Embed(description="Usage: `!setverifyrole @role`", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    verified_roles[gid] = role.id
    save_json(VERIFIED_ROLE_FILE, verified_roles)
    embed = discord.Embed(description=f"Set to {role.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
async def verify(ctx):
    gid = str(ctx.guild.id)
    if gid not in verify_channels:
        embed = discord.Embed(description="No verification setup. Please contact an administrator.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    ch = bot.get_channel(verify_channels[gid])
    if ch:
        embed = discord.Embed(description=f"Please go to {ch.mention} and react with 👋 to verify.", color=discord.Color.blue())
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(description="Channel not found.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command(name="forceverify")
@commands.has_permissions(administrator=True)
async def forceverify(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    if gid not in verified_roles:
        embed = discord.Embed(description="No verified role has been set.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    role = ctx.guild.get_role(verified_roles[gid])
    if not role:
        embed = discord.Embed(description="Verified role not found.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if role in member.roles:
        embed = discord.Embed(description=f"{member.mention} is already verified.", color=discord.Color.blue())
        return await ctx.reply(embed=embed)
    await member.add_roles(role, reason="Force verified by admin")
    embed = discord.Embed(description=f"{member.mention} has been force verified.", color=discord.Color.green())
    await ctx.reply(embed=embed)
    log_embed = discord.Embed(title="Force Verified", description=f"{member.mention} has been force verified by {ctx.author.mention}.", color=discord.Color.green())
    await send_log_embed(ctx.guild, log_embed)

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) == "👋":
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        gid = str(guild.id)
        if gid not in verify_channels or payload.channel_id != verify_channels[gid]:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return
        if gid not in verified_roles:
            return
        role = guild.get_role(verified_roles[gid])
        if not role or role in member.roles:
            return
        try:
            await member.add_roles(role, reason="Verified")
            channel = bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction("👋", member)
            embed = discord.Embed(title="Verified", description=f"{member.mention} has been verified.", color=discord.Color.green())
            await send_log_embed(guild, embed)
        except:
            pass

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        embed = discord.Embed(title="Nickname Changed", color=discord.Color.blue(), timestamp=datetime.now(utc))
        embed.add_field(name="User", value=f"{after} ({after.id})", inline=True)
        embed.add_field(name="Old Nickname", value=before.nick or "None", inline=True)
        embed.add_field(name="New Nickname", value=after.nick or "None", inline=True)
        embed.set_footer(text=after.guild.name)
        await send_log_embed(after.guild, embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Command Not Found", description=f"{ctx.author.mention} attempted to use `{ctx.message.content}` which does not exist.", color=discord.Color.red(), timestamp=datetime.now(utc))
        await send_error_embed(ctx.guild, embed)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You are on cooldown. Try again in {error.retry_after:.2f} seconds.", color=discord.Color.red())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        perms = ', '.join([p.replace('_', ' ').title() for p in error.missing_permissions])
        embed = discord.Embed(description=f"You lack the required permissions: {perms}.", color=discord.Color.red())
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(description=f"Missing required argument: {error.param.name}.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot or message.guild is None:
        return
    embed = discord.Embed(title="Message Deleted", description=message.content[:1000] or "[No text]", color=discord.Color.dark_grey())
    embed.add_field(name="Author", value=message.author.mention, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    await send_log_embed(message.guild, embed)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="Member Joined", color=discord.Color.green(), timestamp=datetime.now(utc))
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
    embed.set_footer(text=member.guild.name)
    await send_log_embed(member.guild, embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.bot or not message.guild:
        return
    if "guess what" in message.content.lower():
        await message.channel.send("idk if i wanna guess tbh")
    if message.guild and message.content.startswith("!"):
        cmd_parts = message.content[1:].split()
        if cmd_parts:
            cmd_name = cmd_parts[0].lower()
            if cmd_name in ["commands", "cmnds"] and message.channel.id != 1480005347266527365 and not message.author.guild_permissions.administrator:
                embed = discord.Embed(description="This command can only be used in the specific bot commands channel.", color=discord.Color.red())
                await message.reply(embed=embed)
                return
    await bot.process_commands(message)

@bot.command()
async def members(ctx):
    num = ctx.guild.member_count
    bots = sum(1 for m in ctx.guild.members if m.bot)
    await ctx.reply(f"This server has {num} members! (including {bots} bots)")

@bot.command()
async def info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description=f"Owner: {guild.owner}\nMembers: {guild.member_count}\nBoosts: {guild.premium_subscription_count}\nCreated: {guild.created_at}")
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(description=f"Slowmode set to {seconds} seconds.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def nick(ctx, target, *, new_nick: str):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.id == PROTECTED_ID:
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    await member.edit(nick=new_nick)
    embed = discord.Embed(description=f"Nickname changed to {new_nick} for {member.mention}", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command(name="remove-nickname")
@commands.has_permissions(administrator=True)
async def remove_nickname(ctx, target):
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if is_protected_action(ctx, member):
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.id == PROTECTED_ID:
        embed = discord.Embed(description="You are not allowed to perform this action on this user.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    await member.edit(nick=None)
    embed = discord.Embed(description=f"Nickname removed for {member.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
async def onlinewhere(ctx):
    servers = []
    for guild in bot.guilds:
        servers.append(f"{guild.name} ({guild.id})")
    server_list = "\n".join(servers) if servers else "No servers found."
    embed = discord.Embed(description=f"This bot is online in the following servers:\n{server_list}", color=discord.Color.blue())
    await ctx.reply(embed=embed)

async def check_economy_command_allowed(ctx):
    if ctx.author.guild_permissions.administrator:
        return True
    gid = str(ctx.guild.id)
    if gid in economy_channels and ctx.channel.id != economy_channels[gid]:
        embed = discord.Embed(description="Economy commands can only be used in the designated channel.", color=discord.Color.red())
        await ctx.reply(embed=embed)
        return False
    return True

jobs = [
    "Odour Judge: Smells breath, feet, and armpits to test product effectiveness.",
    "Dog Food Taster: Evaluates the flavor and texture of pet food.",
    "Professional Bridesmaid: Hired to help brides with planning and support.",
    "Iceberg Mover: Relocates icebergs to protect ships and oil rigs.",
    "Paint Drying Painter: Tests how long new paint mixes take to dry.",
    "Professional Cuddler: Provides therapeutic hugging sessions.",
    "Line Stander: Gets paid to wait in line for products or events.",
    "LEGO Sculptor: Builds models at Legoland Discovery Centres",
    "Golf Ball Diver: Retrieves golf balls from water hazards",
    "Professional Mourner: Hired to weep at funerals."
]

shop_items = {
    "pickaxe": {"price": 1000, "desc": "Increases work coins by 20% for 1 hour."},
    "lucky_charm": {"price": 1500, "desc": "Increases beg coins by 50% for 30 minutes."},
    "thief_gloves": {"price": 2000, "desc": "Increases rob success chance for 1 hour."},
    "gamble_amulet": {"price": 2500, "desc": "Increases gamble win chance by 10% for 1 hour."},
    "bank_safe": {"price": 3000, "desc": "Protects bank from future features."},
    "work_boots": {"price": 3500, "desc": "Reduces work cooldown by 5 seconds permanently."},
    "business_book": {"price": 4000, "desc": "Increases business income by 10% permanently."},
    "stock_market_tip": {"price": 4500, "desc": "One-time double gamble win."},
    "employee_contract": {"price": 5000, "desc": "Allows one extra employee in business."},
    "manager_badge": {"price": 5500, "desc": "Allows hiring one extra manager."}
}

ROB_PROTECTED_IDS = [1401255591749488781, 1468677165250908456]

@bot.command()
@commands.check(check_economy_command_allowed)
@commands.cooldown(1, 20, commands.BucketType.user)
async def work(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    job = random.choice(jobs)
    bonus = (user['work_count'] // 10) * 50
    coins = random.randint(50, 500) + bonus
    user['wallet'] += coins
    user['work_count'] += 1
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"You worked as {job} and earned {coins} coins!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You are on cooldown. Try again in {error.retry_after:.2f} seconds.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def coins(ctx, target = None):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    if target:
        target = await get_target(ctx, target)
        member = await get_member_or_id(ctx, target)
    else:
        member = ctx.author
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    uid = str(member.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    embed = discord.Embed(description=f"{member.display_name} has {user['wallet']} coins in wallet.", color=discord.Color.blue())
    await ctx.reply(embed=embed)

@bot.command(aliases=["balance"])
@commands.check(check_economy_command_allowed)
async def bal(ctx, target = None):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    if target:
        target = await get_target(ctx, target)
        member = await get_member_or_id(ctx, target)
    else:
        member = ctx.author
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    uid = str(member.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    embed = discord.Embed(description=f"{member.display_name}'s Balance:\nWallet: {user['wallet']}\nBank: {user['bank']}", color=discord.Color.blue())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
@commands.cooldown(1, 10800, commands.BucketType.user)
async def rob(ctx, target):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if member.id in ROB_PROTECTED_IDS:
        embed = discord.Embed(description="You cant steal from this user lmao", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    if tuid not in economy_data[gid]['users']:
        economy_data[gid]['users'][tuid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    tuser = economy_data[gid]['users'][tuid]
    if tuser['wallet'] == 0:
        embed = discord.Embed(description="They have no coins in wallet.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    stolen = random.randint(1, tuser['wallet']) if random.random() < 0.5 else 0
    if stolen == 0:
        embed = discord.Embed(description="You got nothing.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] += stolen
    tuser['wallet'] -= stolen
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"You stole {stolen} coins from {member.mention}!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@rob.error
async def rob_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You are on cooldown. Try again in {error.retry_after:.2f} seconds.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
@commands.cooldown(1, 60, commands.BucketType.user)
async def beg(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    coins = random.randint(0, 50)
    if coins == 0:
        embed = discord.Embed(description="No one gave you anything.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] += coins
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"You begged and got {coins} coins!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You are on cooldown. Try again in {error.retry_after:.2f} seconds.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def gamble(ctx, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if amount > 1000 or amount > user['wallet'] or amount <= 0:
        embed = discord.Embed(description="Invalid amount. Max 1000, must have in wallet.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if random.random() < 0.5:
        user['wallet'] += amount
        embed = discord.Embed(description=f"You won {amount} coins!", color=discord.Color.green())
        await ctx.reply(embed=embed)
    else:
        user['wallet'] -= amount
        embed = discord.Embed(description=f"You lost {amount} coins!", color=discord.Color.red())
        await ctx.reply(embed=embed)
    save_json(ECONOMY_FILE, economy_data)

@bot.command()
@commands.check(check_economy_command_allowed)
async def deposit(ctx, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if amount > user['wallet'] or amount <= 0:
        embed = discord.Embed(description="Invalid amount.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] -= amount
    user['bank'] += amount
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Deposited {amount} to bank.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def withdraw(ctx, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if amount > user['bank'] or amount <= 0:
        embed = discord.Embed(description="Invalid amount.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['bank'] -= amount
    user['wallet'] += amount
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Withdrew {amount} to wallet.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def shop(ctx):
    embed = discord.Embed(title="Shop", color=discord.Color.blue())
    for item, data in shop_items.items():
        embed.add_field(name=item, value=f"Price: {data['price']}\n{data['desc']}", inline=False)
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def buy(ctx, *, name: str):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if name not in shop_items:
        embed = discord.Embed(description="Invalid item.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    price = shop_items[name]['price']
    if user['wallet'] < price:
        embed = discord.Embed(description="Not enough coins.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] -= price
    if name not in user['items']:
        user['items'][name] = 0
    user['items'][name] += 1
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Bought {name}!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def inventory(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    embed = discord.Embed(title="Inventory", color=discord.Color.blue())
    for item, count in user['items'].items():
        embed.add_field(name=item, value=count, inline=True)
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def use(ctx, *, name: str):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if name not in user['items'] or user['items'][name] <= 0:
        embed = discord.Embed(description="You don't have this item.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['items'][name] -= 1
    # Assume all items are timed for 1 hour
    duration = 3600
    user['using'][name] = datetime.now(utc).timestamp() + duration
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Used {name} for 1 hour!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def using(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    now = datetime.now(utc).timestamp()
    embed = discord.Embed(title="Using Items", color=discord.Color.blue())
    for item, end_time in list(user['using'].items()):
        if now > end_time:
            del user['using'][item]
            continue
        left = int(end_time - now)
        embed.add_field(name=item, value=f"{left // 60}m left", inline=True)
    save_json(ECONOMY_FILE, economy_data)
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def start_business(ctx, *, name: str):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if user['business_owned']:
        embed = discord.Embed(description="You already own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if user['wallet'] < 20000:
        embed = discord.Embed(description="Not enough coins. Needs 20k.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] -= 20000
    economy_data[gid]['businesses'][name] = {'owner': uid, 'employees': [], 'managers': [], 'stock': 0, 'upgrades': [], 'balance': 0, 'wages': {}}
    user['business_owned'] = name
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Started business {name}!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def business(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    embed = discord.Embed(title="Your Business", color=discord.Color.blue())
    if user['business_owned']:
        biz = economy_data[gid]['businesses'][user['business_owned']]
        embed.add_field(name="Owned", value=user['business_owned'])
        embed.add_field(name="Balance", value=biz['balance'])
        embed.add_field(name="Stock", value=biz['stock'])
        embed.add_field(name="Upgrades", value=", ".join(biz['upgrades']) or "None")
        embed.add_field(name="Employees", value=", ".join([str(e) for e in biz['employees']]) or "None")
        embed.add_field(name="Managers", value=", ".join([str(m) for m in biz['managers']]) or "None")
    embed.add_field(name="Employed in", value=", ".join(user['businesses_employed']) or "None")
    await ctx.reply(embed=embed)

@bot.command(name="business-deposit")
@commands.check(check_economy_command_allowed)
async def business_deposit(ctx, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if amount > user['wallet'] or amount <= 0:
        embed = discord.Embed(description="Invalid amount.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    user['wallet'] -= amount
    economy_data[gid]['businesses'][user['business_owned']]['balance'] += amount
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Deposited {amount} to business.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def stock(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    stock = economy_data[gid]['businesses'][user['business_owned']]['stock']
    embed = discord.Embed(description=f"Your business stock: {stock}", color=discord.Color.blue())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def restocking(ctx, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    cost = amount * 10  # assume cost per stock
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if cost > biz['balance']:
        embed = discord.Embed(description="Not enough business balance.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz['balance'] -= cost
    biz['stock'] += amount
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Restocked {amount} for {cost} coins.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def upgrades(ctx):
    embed = discord.Embed(title="Upgrades", color=discord.Color.blue())
    for upgrade, data in upgrades.items():
        embed.add_field(name=upgrade, value=f"Price: {data['price']}\n{data['effect']}", inline=False)
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def upgrade(ctx, *, upgrade: str):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if upgrade not in upgrades:
        embed = discord.Embed(description="Invalid upgrade.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    price = upgrades[upgrade]['price']
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if price > biz['balance']:
        embed = discord.Embed(description="Not enough business balance.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz['balance'] -= price
    biz['upgrades'].append(upgrade)
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Upgraded {upgrade}!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command(name="set-wage")
@commands.check(check_economy_command_allowed)
async def set_wage(ctx, target, percent: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if tuid not in biz['employees'] and tuid not in biz['managers']:
        embed = discord.Embed(description="User not in business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz['wages'][tuid] = percent
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Set wage for {member.mention} to {percent}%.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def wage(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    embed = discord.Embed(title="Your Wages", color=discord.Color.blue())
    for biz_name in user['businesses_employed']:
        biz = economy_data[gid]['businesses'][biz_name]
        percent = biz['wages'].get(uid, 0)
        embed.add_field(name=biz_name, value=f"{percent}%", inline=True)
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def wages(ctx, *, business: str):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    if business not in economy_data[gid]['businesses']:
        embed = discord.Embed(description="Business not found.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz = economy_data[gid]['businesses'][business]
    embed = discord.Embed(title=f"Wages for {business}", color=discord.Color.blue())
    for euid, percent in biz['wages'].items():
        embed.add_field(name=f"<@{euid}>", value=f"{percent}%", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="hire-employee")
@commands.check(check_economy_command_allowed)
async def hire_employee(ctx, target):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if tuid in biz['employees'] or tuid in biz['managers']:
        embed = discord.Embed(description="User already in business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz['employees'].append(tuid)
    economy_data[gid]['users'][tuid]['businesses_employed'].append(user['business_owned'])
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Hired {member.mention} as employee.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def fire(ctx, target):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if tuid in biz['employees']:
        biz['employees'].remove(tuid)
    elif tuid in biz['managers']:
        biz['managers'].remove(tuid)
    else:
        embed = discord.Embed(description="User not in business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if user['business_owned'] in economy_data[gid]['users'][tuid]['businesses_employed']:
        economy_data[gid]['users'][tuid]['businesses_employed'].remove(user['business_owned'])
    if tuid in biz['wages']:
        del biz['wages'][tuid]
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Fired {member.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command(name="business-leave")
@commands.check(check_economy_command_allowed)
async def business_leave(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['businesses_employed']:
        embed = discord.Embed(description="You are not employed in any business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    for biz_name in list(user['businesses_employed']):
        biz = economy_data[gid]['businesses'][biz_name]
        if uid in biz['employees']:
            biz['employees'].remove(uid)
        if uid in biz['managers']:
            biz['managers'].remove(uid)
        if uid in biz['wages']:
            del biz['wages'][uid]
        user['businesses_employed'].remove(biz_name)
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description="Left all businesses.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command(name="hire-manager")
@commands.check(check_economy_command_allowed)
async def hire_manager(ctx, target):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if not user['business_owned']:
        embed = discord.Embed(description="You don't own a business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    biz = economy_data[gid]['businesses'][user['business_owned']]
    if tuid in biz['employees'] or tuid in biz['managers']:
        embed = discord.Embed(description="User already in business.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    biz['managers'].append(tuid)
    economy_data[gid]['users'][tuid]['businesses_employed'].append(user['business_owned'])
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Hired {member.mention} as manager.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
@commands.cooldown(1, 86400, commands.BucketType.user)
async def cd(ctx):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    coins = random.randint(700, 2000)
    user['wallet'] += coins
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"You claimed {coins} coins from daily!", color=discord.Color.green())
    await ctx.reply(embed=embed)

@cd.error
async def cd_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f"You are on cooldown. Try again in {error.retry_after:.2f} seconds.", color=discord.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
@commands.check(check_economy_command_allowed)
async def gift(ctx, target, amount: int):
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    uid = str(ctx.author.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    if amount > user['wallet'] or amount <= 0:
        embed = discord.Embed(description="Invalid amount.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    tuid = str(member.id)
    if tuid not in economy_data[gid]['users']:
        economy_data[gid]['users'][tuid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    embed = discord.Embed(description=f"{ctx.author.mention} wants to gift {amount} coins to {member.mention}.", color=discord.Color.blue())
    class GiftView(discord.ui.View):
        def __init__(self, sender, receiver, amount):
            super().__init__(timeout=60)
            self.sender = sender
            self.receiver = receiver
            self.amount = amount
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.receiver
        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
            gid = str(interaction.guild.id)
            user = economy_data[gid]['users'][str(self.sender)]
            tuser = economy_data[gid]['users'][str(self.receiver)]
            user['wallet'] -= self.amount
            tuser['wallet'] += self.amount
            save_json(ECONOMY_FILE, economy_data)
            await interaction.response.edit_message(content="Gift accepted!", embed=None, view=None)
            self.stop()
        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(content="Gift declined.", embed=None, view=None)
            self.stop()
    view = GiftView(ctx.author.id, member.id, amount)
    await ctx.reply(embed=embed, view=view)

@bot.command(name="give-coins")
@commands.check(check_economy_command_allowed)
async def give_coins(ctx, target, amount: int):
    if ctx.author.id not in [1468677165250908456, 1401255591749488781]:
        embed = discord.Embed(description="You don't have permission to use this command.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    gid = str(ctx.guild.id)
    if gid not in economy_data:
        economy_data[gid] = {'users': {}, 'businesses': {}}
        save_json(ECONOMY_FILE, economy_data)
    target = await get_target(ctx, target)
    member = await get_member_or_id(ctx, target)
    if not member:
        embed = discord.Embed(description="Invalid user or ID.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    if amount > 10000000000 or amount <= 0:
        embed = discord.Embed(description="Invalid amount. Max 10000000000.", color=discord.Color.red())
        return await ctx.reply(embed=embed)
    uid = str(member.id)
    if uid not in economy_data[gid]['users']:
        economy_data[gid]['users'][uid] = {'wallet': 0, 'bank': 0, 'items': {}, 'using': {}, 'work_count': 0, 'business_owned': None, 'businesses_employed': [], 'last_work': 0, 'last_rob': 0, 'last_beg': 0, 'last_cd': 0}
    user = economy_data[gid]['users'][uid]
    user['wallet'] += amount
    save_json(ECONOMY_FILE, economy_data)
    embed = discord.Embed(description=f"Gave {amount} coins to {member.mention}.", color=discord.Color.green())
    await ctx.reply(embed=embed)

@bot.command()
async def myroles(ctx):
    roles = [r.mention for r in ctx.author.roles if r.name != "@everyone"]
    if not roles:
        embed = discord.Embed(description="You have no roles.", color=discord.Color.blue())
        return await ctx.reply(embed=embed)
    per_page = 10
    pages = [roles[i:i + per_page] for i in range(0, len(roles), per_page)]
    embeds = []
    for idx, page in enumerate(pages, 1):
        embed = discord.Embed(title=f"📄Your Roles - Page {idx}/{len(pages)}", description="\n".join(page), color=discord.Color.blue())
        embeds.append(embed)
    await paginate(ctx, embeds)

@bot.command()
async def roles(ctx):
    roles = [r.mention for r in ctx.guild.roles[::-1] if r.name != "@everyone"]
    if not roles:
        embed = discord.Embed(description="No roles in server.", color=discord.Color.blue())
        return await ctx.reply(embed=embed)
    per_page = 10
    pages = [roles[i:i + per_page] for i in range(0, len(roles), per_page)]
    embeds = []
    for idx, page in enumerate(pages, 1):
        embed = discord.Embed(title=f"📄Server Roles - Page {idx}/{len(pages)}", description="\n".join(page), color=discord.Color.blue())
        embeds.append(embed)
    await paginate(ctx, embeds)


bot.run(os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN"))
