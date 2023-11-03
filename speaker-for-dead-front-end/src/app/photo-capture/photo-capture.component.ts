import { Component, ElementRef, ViewChild, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-photo-capture',
  templateUrl: './photo-capture.component.html',
  styleUrls: ['./photo-capture.component.scss']
})
export class PhotoCaptureComponent {

  //access child elements components in the template and interact with them in this parent component
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;
  @ViewChild('photoElement') photoElement!: ElementRef<HTMLImageElement>;

  //custom event
  @Output() imageBlobEvent = new EventEmitter<Blob>();

  //instance variables
  private mediaStream: MediaStream | null = null;

  constructor() {}

  //called after the view of the component has been initialized. Component's view, inc 
  //its child components, has been fully set up and rendered.
  async ngAfterViewInit() {
    try {
      //access device camera
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      console.log(this.mediaStream);
      this.videoElement.nativeElement.srcObject = this.mediaStream;
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  }

  //called just before the component is destroyed or removed from the DOM
  ngOnDestroy() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
    }
  }

  //take photo on user click
  capturePhoto() {
    
    //gather DOM elements
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
