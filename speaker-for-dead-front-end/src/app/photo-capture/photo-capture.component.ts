import { Component, ElementRef, ViewChild, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-photo-capture',
  templateUrl: './photo-capture.component.html',
  styleUrls: ['./photo-capture.component.scss']
})
export class PhotoCaptureComponent {

  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;
  @ViewChild('photoElement') photoElement!: ElementRef<HTMLImageElement>;

  @Output() imageBlobEvent = new EventEmitter<Blob>();

  private mediaStream: MediaStream | null = null;

  constructor() {}

  /*async ngAfterViewInit() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoElement.nativeElement.srcObject = stream;
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  }*/

  async ngAfterViewInit() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoElement.nativeElement.srcObject = this.mediaStream;
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  }

  ngOnDestroy() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
    }
  }


  capturePhoto() {
    
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const photo = this.photoElement.nativeElement;

    // Pause the video to freeze the frame
    video.pause();

    // Draw the current video frame onto the canvas
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context!.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas content to a data URL and set it as the image source
    photo.src = canvas.toDataURL('image/jpeg');
    
    // Convert the canvas content to a blob
    canvas.toBlob((blob: Blob | null) => {
      if (blob) {
        // Emit the image blob to the parent component
        this.imageBlobEvent.emit(blob);
      }
    }, 'image/jpeg');

    // Resume the video
    video.play();

  }


  

}
