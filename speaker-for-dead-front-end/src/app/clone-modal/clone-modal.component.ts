import { Component, Input, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { ChangeDetectorRef } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { VoiceReconComponent } from '../voice-recon/voice-recon.component';

@Component({
  selector: 'app-clone-modal',
  templateUrl: './clone-modal.component.html',
  styleUrls: ['./clone-modal.component.scss']
})
export class CloneModalComponent {
  
  //pass data from parent components to this child component. 
  @Input() item: any; 
  @Input() idleVideo: any;
  @Input() talkingVideo: any;

  //access child elements components in the template and interact with them in this parent component
  @ViewChild('customCloneVideoElement', { static: false }) customCloneVideoElement: ElementRef | undefined;
  @ViewChild('voiceRecon', { static: false }) voiceRecon!: VoiceReconComponent;

  //instance variables
  audioStreamStarted = false;
  currentVideo: string | undefined;
  textToSend: string | undefined;
  responseText: string | undefined;
  seekLoadAndPlayCount: number= 0;
  showTextChat: boolean = true;
  showVoiceChat: boolean = false;
  buttonLabel: string = 'Change To Voice To Voice Chat Session';
  alertLabel: string = 'Current Chat Style: Text to Voice';
  currentResponse: string = '';


  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef, private socket: Socket) {}

  toggleChatStyle() {
    this.showTextChat = !this.showTextChat;
    this.showVoiceChat = !this.showVoiceChat;
    this.buttonLabel = this.showTextChat ? 'Change To Voice To Voice Chat Session' : 'Change To Text To Voice Chat Session';
    this.alertLabel = this.showTextChat ? 'Current Chat Style: Text to Voice' : 'Current Chat Style: Voice to Voice';
  }

  ngOnInit(): void {
    //init current video as idle video
    this.currentVideo = this.idleVideo;
    // Subscribe to the 'audio_stream_started' channel
    this.socket.fromEvent('audio_stream_started').subscribe((data) => {
      console.log('Received custom clone audio stream started: ', data);
      this.audioStreamStarted = true;
      this.currentVideo = this.talkingVideo;
      console.log(this.currentVideo);
      this.seekLoadAndPlay(this.customCloneVideoElement, true);
      
    });
  }
  
  ngOnDestroy(): void{ //if the modal is closed and voice recon is still running then stop the voice recon service
    if(this.voiceRecon != undefined && this.voiceRecon.isStartButtonDisabled){
      console.log("stopping voice recon due to modal closing");
      this.voiceRecon.stopService();
    }
  }

  restartVoiceReconDueToSilence(){ //allow user to manually restart the service if they are silent too long and voice recon shuts off
    if(this.voiceRecon != undefined && this.voiceRecon.isStartButtonDisabled){
      this.voiceRecon.startService();
    }
  }

  // Method to seek to the beginning, load, and optionally play the appropriate video
  seekLoadAndPlay(element: ElementRef | undefined, playVideo: boolean = false): void {
    
    if (element && element.nativeElement instanceof HTMLVideoElement) {

      if(this.showVoiceChat){ 
        this.seekLoadAndPlayCount++;
      }
      
      //the voice recon service needs to be restarted when the idle video begins to play after response
      if(this.seekLoadAndPlayCount % 2 === 0 && this.showVoiceChat){
         console.log("restarting voice recon service");
         this.voiceRecon.startService();
      }
      
      const videoElement: HTMLVideoElement = element.nativeElement;
      videoElement.currentTime = 0; // Seek to the beginning
      videoElement.load(); // Load the updated video

      if (playVideo) {
        console.log("made it to play");
        //videoElement.play(); // Play the updated video
        
      }

      this.cdRef.detectChanges();
       
    } else {
      console.warn('Element is undefined or not an HTMLVideoElement.');
    }
  }

  sendAndReceiveText(cloneName: string, voiceID: string): void {
    const apiUrl = 'http://localhost:5000/api/custom_clone_chat';  
    console.log(cloneName + ' ' + this.textToSend + ' ' + voiceID);
    const data = { name: cloneName, text: this.textToSend, customVoiceID: voiceID };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        this.currentVideo = this.idleVideo;
        this.seekLoadAndPlay(this.customCloneVideoElement, false);
        console.log(response.response_text);
        this.currentResponse = response.response_text;
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
    
  }

  sendMessageToCloneVoiceRecon(prompt: string, cloneName: string, voiceID: string){
      
      console.log(prompt + ' ' + cloneName + ' ' + voiceID);
      const apiUrl = 'http://localhost:5000/api/custom_clone_chat';  
      const data = { name: cloneName, text: prompt, customVoiceID: voiceID };

      this.http.post<any>(apiUrl, data).subscribe(
       (response) => {
        this.responseText = response.response_text; // Store the response text
        this.currentVideo = this.idleVideo;
        this.seekLoadAndPlay(this.customCloneVideoElement, false);  
        console.log(response.response_text);
        this.currentResponse = response.response_text;
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );

  }
  
}
