import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { ChangeDetectorRef } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { trigger, state, style, transition, animate } from '@angular/animations';

@Component({
  selector: 'app-interact',
  templateUrl: './interact.component.html',
  styleUrls: ['./interact.component.scss'],
  animations: [
    trigger('flipState', [
      state('active', style({
        transform: 'rotateY(179deg)'
      })),
      state('inactive', style({
        transform: 'rotateY(0)'
      })),
      transition('active => inactive', animate('500ms ease-out')),
      transition('inactive => active', animate('500ms ease-in'))
    ])
  ]
})

export class InteractComponent implements OnInit {

  @ViewChild('videoElement', { static: false }) videoElement: ElementRef | undefined;
  @ViewChild('lowLatencyElement', { static: false }) lowLatencyElement: ElementRef | undefined;
  @ViewChild('audioFileInput') audioFileInput!: ElementRef;
  @ViewChild('imageFileInput') imageFileInput!: ElementRef;
  @ViewChild('contextFileInput') contextFileInput!: ElementRef;

  //front end instance vars
  isVideoClone: boolean = true;
  isCloneTypeButtonDisabled: boolean = false;
  flip: string = 'inactive';
  
  //Mark Billinghurst clone instance vars
  textToSend: string | undefined;
  responseText: string | undefined;
  responseVideo: string | undefined;
  videoIsGenerating = false;
  audioStreamStarted = false;
  
  //Clone creation instance vars
  maxAudioFileSizeMB = 10;
  audioName: string = '';
  voiceTrainedSuccessfully = false;
  videosTrainedSuccessfully = false;
  progressValue: number = 0;
  audioFileSelected = false;
  imageFileSelected = false;
  contextFileSelected = false;

  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef, private socket: Socket) {}

  ngOnInit(): void {
      // Subscribe to the 'audio_stream_started' channel
    this.socket.fromEvent('audio_stream_started').subscribe((data) => {
      console.log('Received audio stream started:', data);
      this.audioStreamStarted = true;
      this.responseVideo = "../assets/video/mark-talking.mp4";
      this.seekLoadAndPlay(this.lowLatencyElement, true);
    });

    // Subscribe to the 'voice_trained_successfully' channel
    this.socket.fromEvent('voice_trained_successfully').subscribe((data) => {
      console.log('voice trained successfully:', data);
      this.voiceTrainedSuccessfully = true;
      this.progressValue = 40;
      
    });

    // Subscribe to the 'voice_trained_successfully' channel
    this.socket.fromEvent('videos_trained_successfully').subscribe((data) => {
      console.log('videos trained successfully:', data);
      this.videosTrainedSuccessfully = true;
      this.progressValue = 100;
      
    });

  }

  //FRONT END METHODS
  toggleFlip() {
    this.flip = (this.flip == 'inactive') ? 'active' : 'inactive';
  }
  
  toggleCloneType(): void {
    this.isVideoClone = !this.isVideoClone;
  }

  //MARK BILLINGHURST CLONE METHODS 

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
    this.videoIsGenerating = true;
    console.log("video is generating " + this.videoIsGenerating);
    this.isCloneTypeButtonDisabled = true;
    const apiUrl = 'http://localhost:5000/api/data_video';  
    const data = { text: this.textToSend };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.videoIsGenerating = false;
        this.responseText = response.response_text; // Store the response text
        this.responseVideo = response.response_video; // custom lip syncing video from ML API
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

  //TRAIN CUSTOM VOICE METHODS 

  addVoiceAndImage(): void {

    const audioFile = this.audioFileInput.nativeElement.files[0];
    const imageFile = this.imageFileInput.nativeElement.files[0];
    const contextFile = this.contextFileInput.nativeElement.files[0];
    this.progressValue = 10;
    
    if (audioFile && imageFile) {
      const apiUrl = 'http://localhost:5000/api/train_clone';

      // Create a FormData object to send the file as a multi-part form data
      const formData = new FormData();
      formData.append('audioFile', audioFile);  
      formData.append('name', this.audioName);
      formData.append('imageFile', imageFile);
      formData.append('contextFile', contextFile);

      // Send the FormData object to the server
      this.http.post(apiUrl, formData).subscribe(
        (response) => {
          console.log('Clone trained!', response);
        },
        (error) => {
          console.error('Error occurred:', error);
        }
      );
    }

  }

  //clone creation form validation methods
  onAudioFileSelected(event: any) {
    
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      // Check if the selected file exceeds the maximum size
      const fileSizeMB = selectedFile.size / (1024 * 1024); // Convert to megabytes
      if (fileSizeMB > this.maxAudioFileSizeMB) {
        alert(`File size exceeds the maximum allowed (${this.maxAudioFileSizeMB} MB).`);
        this.clearFileInput();
      } else {
        console.log('Selected file:', selectedFile);
        this.audioFileSelected = true;
      }
    }
  }

  onImageFileSelected(event: any) {
    const selectedfile = event.target.files[0];
    if(selectedfile){
      this.imageFileSelected = true;
    }
  }

   onNameSelected(event: any) {
      this.audioName = this.audioName.replace(/\s/g, '');
  }

  onContextFileSelected(event: any) {
    const selectedfile = event.target.files[0];
    if(selectedfile){
      this.contextFileSelected = true;
    }
  }

  clearFileInput() {
    // Reset the file input and clear the selected file
    this.audioFileInput.nativeElement.value = '';
  }
  
} //close class 
