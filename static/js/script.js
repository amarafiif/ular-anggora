document.addEventListener("DOMContentLoaded", function () {
	const video = document.getElementById("video");
	const captureButton = document.getElementById("capture");
	const registerForm = document.getElementById("register-form");

	// Mendapatkan akses ke kamera saat halaman dimuat
	navigator.mediaDevices
		.getUserMedia({ video: true })
		.then(function (stream) {
			video.srcObject = stream;
		})
		.catch(function (err) {
			console.error("Error accessing the camera: ", err);
		});

	// Menangani klik tombol "Capture"
	captureButton.addEventListener("click", function (event) {
		event.preventDefault();
		const canvas = document.createElement("canvas");
		const context = canvas.getContext("2d");

		// Menggunakan lebar dan tinggi video untuk menetapkan ukuran canvas
		canvas.width = video.videoWidth;
		canvas.height = video.videoHeight;

		// Menggambar frame video ke dalam canvas
		context.drawImage(video, 0, 0, canvas.width, canvas.height);

		// Mengonversi gambar canvas ke dalam bentuk data URL base64
		const imageData = canvas.toDataURL("image/jpeg");

		// Menyimpan data URL base64 ke dalam input tersembunyi
		// Buat input hidden untuk menyimpan image base64
		let imageInput = document.getElementById("image");
		if (!imageInput) {
			imageInput = document.createElement("input");
			imageInput.type = "hidden";
			imageInput.name = "image";
			imageInput.id = "image";
			registerForm.appendChild(imageInput);
		}
		imageInput.value = imageData;
	});

	// Menangani submit form registrasi
	registerForm.addEventListener("submit", function (event) {
		event.preventDefault();
		const formData = new FormData(registerForm);

		fetch("/register", {
			method: "POST",
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				alert(data.message);
			})
			.catch((error) => {
				console.error("Error registering user: ", error);
				alert("An error occurred while registering user.");
			});
	});

	// Menangani klik tombol "Train Model"
	document.getElementById("train-model").addEventListener("click", function () {
		fetch("/train", {
			method: "POST",
		})
			.then((response) => response.json())
			.then((data) => {
				alert(data.message);
			})
			.catch((error) => {
				console.error("Error training model: ", error);
				alert("An error occurred while training model.");
			});
	});
});
