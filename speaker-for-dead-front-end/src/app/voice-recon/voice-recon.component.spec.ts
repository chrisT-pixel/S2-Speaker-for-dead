import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VoiceReconComponent } from './voice-recon.component';

describe('VoiceReconComponent', () => {
  let component: VoiceReconComponent;
  let fixture: ComponentFixture<VoiceReconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VoiceReconComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VoiceReconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
