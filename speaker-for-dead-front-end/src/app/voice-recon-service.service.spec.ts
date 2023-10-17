import { TestBed } from '@angular/core/testing';

import { VoiceReconServiceService } from './voice-recon-service.service';

describe('VoiceReconServiceService', () => {
  let service: VoiceReconServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VoiceReconServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
