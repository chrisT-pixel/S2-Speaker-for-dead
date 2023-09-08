import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { ChangeDetectorRef } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Component({
  selector: 'app-interact',
  templateUrl: './interact.component.html',
  styleUrls: ['./interact.component.scss']
})

export class InteractComponent implements OnInit {
//export class InteractComponent{

  @ViewChild('videoElement', { static: false }) videoElement: ElementRef | undefined;
  @ViewChild('lowLatencyElement', { static: false }) lowLatencyElement: ElementRef | undefined;

  textToSend: string | undefined;
  responseText: string | undefined;
  responseVideo: string | undefined;
  isVideoClone: boolean = true;
  isCloneTypeButtonDisabled: boolean = false;
  audioStreamStarted = false;

  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef, private socket: Socket) {}

  ngOnInit(): void {
    // Subscribe to the 'audio_stream_started' channel
    this.socket.fromEvent('audio_stream_started').subscribe((data) => {
    console.log('Received audio stream started:', data);
    this.audioStreamStarted = true;
    this.responseVideo = "../assets/video/mark-talking.mp4";
    this.seekLoadAndPlay(this.lowLatencyElement, true);
    });
  }
  

  toggleCloneType(): void {
    this.isVideoClone = !this.isVideoClone;
  }

  // Method to seek to the beginning, load, and optionally play the element
  seekLoadAndPlay(element: ElementRef | undefined, playVideo: boolean = false): void {
    if (element && element.nativeElement instanceof HTMLVideoElement) {
      const videoElement: HTMLVideoElement = element.nativeElement;
      videoElement.currentTime = 0; // Seek to the beginning
      videoElement.load(); // Load the updated video

      if (playVideo) {
        videoElement.play(); // Play the updated video
      }

      this.cdRef.detectChanges();
    } else {
      console.warn('Element is undefined or not an HTMLVideoElement.');
    }
  }
   
  sendAndReceiveText(): void {
    
    this.isCloneTypeButtonDisabled = true;
    const apiUrl = 'http://localhost:5000/api/data';  
    const data = { text: this.textToSend };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        this.responseVideo = "../assets/video/mark-idle.mp4";
        this.seekLoadAndPlay(this.lowLatencyElement, false);  
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
    
  }

  sendAndReceiveTextVideo(): void {
    this.isCloneTypeButtonDisabled = true;
    const apiUrl = 'http://localhost:5000/api/data_video';  
    const data = { text: this.textToSend };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        this.responseVideo = response.response_video;
        // Seek to the beginning of the video and play
        this.seekLoadAndPlay(this.videoElement, true);
          
        this.videoElement!.nativeElement.addEventListener('ended', () => {
          // This function will be executed when the video ends
          console.log('Video has finished playing');
          this.responseVideo = "../assets/video/mark-idle.mp4";
          this.seekLoadAndPlay(this.videoElement, false);
        });
        
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
  }
  
}
