import { Component, Input, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { ChangeDetectorRef } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Component({
  selector: 'app-clone-modal',
  templateUrl: './clone-modal.component.html',
  styleUrls: ['./clone-modal.component.scss']
})
export class CloneModalComponent {
  
  @Input() item: any; // Inputs to receive clone data
  @Input() idleVideo: any;
  @Input() talkingVideo: any;

  @ViewChild('customCloneVideoElement', { static: false }) customCloneVideoElement: ElementRef | undefined;

  audioStreamStarted = false;
  currentVideo: string | undefined;
  //customVoiceID: string | undefined;
  textToSend: string | undefined;
  responseText: string | undefined;

  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef, private socket: Socket) {}

  ngOnInit(): void {
    //init current video as idle video
    this.currentVideo = this.idleVideo;
    //this.customVoiceID = this.item.voiceID;
    // Subscribe to the 'custom_clone_audio_stream_started' channel
    this.socket.fromEvent('custom_clone_audio_stream_started').subscribe((data) => {
      console.log('Received custom clone audio stream started:', data);
      this.audioStreamStarted = true;
      this.currentVideo = this.talkingVideo;
      this.seekLoadAndPlay(this.customCloneVideoElement, true);
    });
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

  sendAndReceiveText(cloneName: string, voiceID: string): void {
    const apiUrl = 'http://localhost:5000/api/custom_clone_chat';  
    console.log(cloneName + this.textToSend + voiceID);
    const data = { name: cloneName, text: this.textToSend, customVoiceID: voiceID };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        this.currentVideo = this.idleVideo;
        this.seekLoadAndPlay(this.customCloneVideoElement, false);  
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
    
  }
  
}
