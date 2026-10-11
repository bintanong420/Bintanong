# Historical development-state snapshot

Source: `codex_takeover_2026-10-10/platform_state.json`. Source SHA-256: `fa6fdfb641f78463bfae4cbb690602dab8f5f12eeeb87e6318ed7be1d36acf27`. Imported 11 October 2026. This is a historical record, not current authorization or formal phase state. The JSON body below is preserved; raw operational artifacts remain external.

````json
{
  "timestamp": "2026-10-09T19:20:15.330128+00:00",
  "usage": {
    "file": "C:\\Users\\Hawksprey\\.codex\\sessions\\2026\\10\\10\\rollout-2026-10-10T02-58-24-01a12207-e1b0-78e3-a012-fd7a86447109.jsonl",
    "timestamp": "2026-10-09T19:19:45.177Z",
    "rate_limits": {
      "limit_id": "codex",
      "limit_name": null,
      "primary": {
        "used_percent": 86.0,
        "window_minutes": 300,
        "resets_at": 1791574105
      },
      "secondary": {
        "used_percent": 42.0,
        "window_minutes": 10080,
        "resets_at": 1791972130
      },
      "credits": {
        "has_credits": false,
        "unlimited": false,
        "balance": "0"
      },
      "individual_limit": null,
      "spend_control_reached": null,
      "plan_type": "plus",
      "rate_limit_reached_type": null
    }
  },
  "worktrees": {
    "exit": 0,
    "output": "worktree C:/Users/Hawksprey/source/repos/Bintanong\nHEAD 0caeaba8d8221a0f75b154e94bc3167b780f1407\nbranch refs/heads/dev\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/b2\nHEAD bc4702cd6a77f630204128768f09cc9706bc7c0a\nbranch refs/heads/feat/prospectus-phase-b2-section-fixer\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/d-baseline-641523d\nHEAD 641523d212839084da03d966ffbfca66c7e83e42\ndetached\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/draft-f\nHEAD dd699958505996358864383ff9c184cb98aec985\nbranch refs/heads/draft/phase-f-tools-cli\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/draft-p2\nHEAD ef0cdbff9dca3af7a9f80fdd3036a701c61c2a3c\nbranch refs/heads/draft/phase-02-code\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/draft-session\nHEAD 3e0d6b361d83a965bf900dd6a41d6ea5c274bf54\nbranch refs/heads/draft/session-lifecycle\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/formal-plans\nHEAD 4d780b721a81a34cc8ca6ea7842c888f6ce9d259\nbranch refs/heads/docs/phase-1-2-preparation-20261007\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/gui\nHEAD 61d251da47e29ca776073b44bf68202488bcb555\nbranch refs/heads/feat/prospectus-review-gui\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/gui-fixes\nHEAD fa38bb895f5152f84af6f38cb07d66f525aa35ba\nbranch refs/heads/feat/review-gui-fixes-20261007\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/gui-plan\nHEAD 4ebbc7810841701093b6e4f8e7e376d3f9bc10b5\nbranch refs/heads/docs/prospectus-review-gui-plan\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/gui-t10\nHEAD cd8870680835fdb85dc72ccc2e0c1b8bb2eaeab1\nbranch refs/heads/feat/prospectus-gui-task10\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/integration\nHEAD 5c34fd73adbd2806d6c48362eb248b74921fb79c\nbranch refs/heads/integration/prospectus-0710\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/integration-e\nHEAD 3e19bd3649638cd0b572dc257eb651036c7f8991\nbranch refs/heads/integration/phase-e-0810\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/integration-fin\nHEAD 0caeaba8d8221a0f75b154e94bc3167b780f1407\nbranch refs/heads/integration/finished-1010\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/integration-gui\nHEAD cf8b11c566d76bd5048a761a169907aee31a242b\nbranch refs/heads/integration/gui-0710\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/ocr\nHEAD f9e0dbc784552afd6ae303c4d5f326c1d30c57ee\nbranch refs/heads/feat/ocr-measurement-harness\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-1\nHEAD 00f1fb14576f648195f69796de07e534c7d1eed9\nbranch refs/heads/feat/phase-01-source-governance-contracts\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-2\nHEAD adf5d5192396dd18e58174add83773f2a0ce4aaa\nbranch refs/heads/feat/phase-02-document-ingestion-plan\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-c\nHEAD e3e3526f08e60baf4dc5acdaddef665a41b391bc\nbranch refs/heads/feat/prospectus-phase-c-status-separation\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d\nHEAD 80dd71802ceb1e9f1905faa4f7416952e902be04\nbranch refs/heads/feat/prospectus-phase-d-safe-cache\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-e\nHEAD ec0eac7cb025722331cd2eb216e0f925c2912658\nbranch refs/heads/feat/prospectus-phase-e-rag-provenance\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/publish-a-d\nHEAD 4d780b721a81a34cc8ca6ea7842c888f6ce9d259\nbranch refs/heads/publish/prospectus-a-d-20261007\n\nworktree C:/Users/Hawksprey/source/repos/Bintanong-wt/task13\nHEAD 356f8a9d45bc5f7538229b9a1b4bc1a3433dea4b\nbranch refs/heads/feat/prospectus-b2-banner-split",
    "error": ""
  },
  "owner_status": {
    "exit": 0,
    "output": " M .gitignore\n?? plans/CLAUDE_CODE_HANDOFF_prospectus_phase2_2026-10-07.md\n?? plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md\n?? plans/phase2_prospectus_master_status_2026-10-07.md",
    "error": ""
  },
  "drafts": {
    "integration-fin": {
      "tip": {
        "exit": 0,
        "output": "0caeaba8d8221a0f75b154e94bc3167b780f1407",
        "error": ""
      },
      "status": {
        "exit": 0,
        "output": "",
        "error": ""
      }
    },
    "draft-f": {
      "tip": {
        "exit": 0,
        "output": "dd699958505996358864383ff9c184cb98aec985",
        "error": ""
      },
      "status": {
        "exit": 0,
        "output": "",
        "error": ""
      }
    },
    "draft-p2": {
      "tip": {
        "exit": 0,
        "output": "ef0cdbff9dca3af7a9f80fdd3036a701c61c2a3c",
        "error": ""
      },
      "status": {
        "exit": 0,
        "output": "",
        "error": ""
      }
    },
    "draft-session": {
      "tip": {
        "exit": 0,
        "output": "3e0d6b361d83a965bf900dd6a41d6ea5c274bf54",
        "error": ""
      },
      "status": {
        "exit": 0,
        "output": "",
        "error": ""
      }
    }
  },
  "alienista": {
    "worktrees": {
      "exit": 0,
      "output": "worktree C:/Users/Hawksprey/source/repos/Alienista-\nHEAD 7f1cc9bf9efd2997390557dc3600c82406e8f7ed\nbranch refs/heads/dev\n\nworktree C:/Users/Hawksprey/source/repos/Alienista-audit-repair\nHEAD 7a093689fccbac9361168b699954cb559d694445\nbranch refs/heads/fix/security-offline-ui",
      "error": ""
    },
    "status": {
      "exit": 0,
      "output": "",
      "error": ""
    },
    "tip": {
      "exit": 0,
      "output": "7f1cc9bf9efd2997390557dc3600c82406e8f7ed",
      "error": ""
    }
  }
}

````
