async function scrollAndExtractVideosWithDebug() {
	let prevVideoCount = 0;

	// Scroll until all videos are loaded
	while (true) {
		window.scrollTo(0, document.documentElement.scrollHeight);
		await new Promise((resolve) => setTimeout(resolve, 2000)); // Wait for new content to load

		// Count the number of loaded videos
		let videos = document.querySelectorAll('ytd-playlist-video-renderer');
		console.log(`Videos loaded: ${videos.length}`);

		if (videos.length === prevVideoCount) break; // Exit if no new videos loaded
		prevVideoCount = videos.length;
	}

	console.log(`Finished scrolling! Total videos detected: ${prevVideoCount}`);

	// Extract video data
	let videoElements = Array.from(
		document.querySelectorAll('ytd-playlist-video-renderer'),
	);
	let data = videoElements.map((video, index) => {
		let title =
			video.querySelector('#video-title')?.textContent.trim() ||
			'Unknown Title';
		let link = video.querySelector('#video-title')?.href || '#';
		let ariaLabel = video.querySelector('h3')?.getAttribute('aria-label') || '';
		let channelName =
			video.querySelector('.ytd-channel-name #tooltip').textContent.trim() ||
			'no name';
		let thumbnail =
			video.querySelector('.ytCoreImageHost').getAttribute('src') ||
			'No Thumbnail';
		return { index: index + 1, title, link, thumbnail, ariaLabel, channelName };
	});

	console.log(`Extracted ${data.length} videos.`);
	console.log(JSON.stringify(data, null, 2));
	return data;
}

scrollAndExtractVideosWithDebug();
