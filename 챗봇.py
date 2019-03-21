import discord
import asyncio
import youtube_dl
import re

client = discord.Client()
que = {}
playerlist = {}
playlist = list() #재생목록 리스트

def queue(id): #음악 재생용 큐
	if que[id] != []:
		player = que[id].pop(0)
		playerlist[id] = player
		del playlist[0]
		player.start()

@client.event 
async def on_ready(): #봇이 준비되었을 때 출력할 내용
	print(client.user.name)
	print(client.user.id)

@client.event
async def on_message(message):

	if message.author == client.user: #봇이 채팅을 쳤을 때 명령어로 인식되지 않음
		return

	if message.content == "!안녕":
		em = discord.Embed(title="안녕",description="안녕",url ="http://google.com", colour=0xDEADBF)
		em.add_field(name="안녕",value="[안녕](http://google.com)")
		await client.send_message(message.channel, embed=em)

	if message.content.startswith("!음악"): #음성채널에 봇을 추가 및 음악 재생
		msg = message.content.split(" ")
		try:
			url = msg[1]
			url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', url) #정규 표현식을 사용해 url 검사
			if url1 == None:
				await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: url을 제대로 입력해주세요.",colour = 0x2EFEF7))
				return
		except IndexError:
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: url을 입력해주세요.",colour = 0x2EFEF7))
			return

		channel = message.author.voice.voice_channel 
		server = message.server
		voice_client = client.voice_client_in(server)

		if client.is_voice_connected(server) and not playerlist[server.id].is_playing(): #봇이 음성채널에 접속해있으나 음악을 재생하지 않을 때
			await voice_client.disconnect()
		elif client.is_voice_connected(server) and playerlist[server.id].is_playing(): #봇이 음성채널에 접속해있고 음악을 재생할 때
			player = await voice_client.create_ytdl_player(url,after=lambda:queue(server.id),before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
			if server.id in que: #큐에 값이 들어있을 때
				que[server.id].append(player)
			else: #큐에 값이 없을 때
				que[server.id] = [player]
			await client.send_message(message.channel, embed=discord.Embed(title=":white_check_mark: 추가 완료!",colour = 0x2EFEF7))
			playlist.append(player.title) #재생목록에 제목 추가
			return

		try:
			voice_client = await client.join_voice_channel(channel)
		except discord.errors.InvalidArgument: #유저가 음성채널에 접속해있지 않을 때
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: 음성채널에 접속하고 사용해주세요.",colour = 0x2EFEF7))
			return

		try:
			player = await voice_client.create_ytdl_player(url,after=lambda:queue(server.id),before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
			playerlist[server.id] = player
			playlist.append(player.title)
		except youtube_dl.utils.DownloadError: #유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.",colour = 0x2EFEF7))
			await voice_client.disconnect()
			return
		player.start()

	if message.content == "!종료": #음성채널에서 봇을 나가게 하기
		server = message.server
		voice_client = client.voice_client_in(server)

		if voice_client == None: #봇이 음성채널에 접속해있지 않았을 때
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: 봇이 음성채널에 없어요.",colour = 0x2EFEF7))
			return
		
		await client.send_message(message.channel, embed=discord.Embed(title=":mute: 채널에서 나갑니다.",colour = 0x2EFEF7)) #봇이 음성채널에 접속해있을 때
		await voice_client.disconnect()

	if message.content == "!스킵":
		id = message.server.id
		if not playerlist[id].is_playing(): #재생 중인 음악이 없을 때
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: 스킵할 음악이 없어요.",colour = 0x2EFEF7))
			return
		await client.send_message(message.channel, embed=discord.Embed(title=":mute: 스킵했어요.",colour = 0x2EFEF7))
		playerlist[id].stop()
	
	if message.content == "!목록":

		if playlist == []:
			await client.send_message(message.channel, embed=discord.Embed(title=":no_entry_sign: 재생목록이 없습니다.",colour = 0x2EFEF7))
			return

		playstr = "```css\n[재생목록]\n\n"
		for i in range(0, len(playlist)):
			playstr += str(i+1)+" : "+playlist[i]+"\n"
		await client.send_message(message.channel, playstr+"```")

client.run('토큰')