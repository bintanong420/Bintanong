import test from 'node:test';
import assert from 'node:assert/strict';
import { confirmedDetails, followUpMessage } from '../lib/student-clarification.ts';
import { createWorkspace, workspaceReducer as reduce } from '../lib/student-workspace.ts';

const scope={programId:'program-a',curriculumId:'curriculum-a'};
const curricula=[{...scope,programName:'Synthetic program',curriculumName:'Reviewed edition'}];
const answer={status:'clarification_needed',language:'en',missingFields:['course_status'],clarification:{scope,courses:[{code:'Z4/L',kind:'completion'},{code:'Z3/L',kind:'completion'}]}};

test('only explicitly confirmed supported choices can be reused, without silently attaching them',()=>{
  const details=confirmedDetails(answer,curricula,{'completion:Z4/L':{value:'not_passed',explanation:''},'completion:Z3/L':{value:'unknown',explanation:''}},scope);
  assert.equal(details.length,2);
  assert.equal(followUpMessage('What can I do next?',scope,details,[]),'What can I do next?');
  assert.equal(followUpMessage('What can I do next?',scope,details,['completion:Z4/L','completion:Z3/L']),
    'What can I do next?\n\nI have not passed Z4/L.\nI do not know whether I have passed Z3/L.');
  assert.equal(confirmedDetails(answer,curricula,{},scope).length,0);
  assert.equal(confirmedDetails(answer,curricula,{'completion:INVENTED':{value:'passed',explanation:''}},scope).length,0);
  assert.equal(confirmedDetails(answer,curricula,{'completion:Z4/L':{value:'passed',explanation:''}},null).length,0);
});

test('remembering choices replaces the same course condition and cleanup leaves the conversation intact',()=>{
  const first=confirmedDetails(answer,curricula,{'completion:Z4/L':{value:'passed',explanation:''},'completion:Z3/L':{value:'unknown',explanation:''}},scope);
  let state=reduce({...createWorkspace(),draft:'A question'},{type:'submit',id:'a'});
  state=reduce(state,{type:'remember',details:first});
  assert.equal(state.supplied.length,2);
  state=reduce(state,{type:'remember',details:[{...first[0],label:'Not passed',text:'I have not passed Z4/L.'}]});
  assert.equal(state.supplied.length,2);
  assert.equal(state.supplied.find(d=>d.code==='Z4/L').text,'I have not passed Z4/L.');
  const forgotten=reduce(state,{type:'forget-details'});
  assert.deepEqual(forgotten.supplied,[]);
  assert.equal(forgotten.messages,state.messages);
  assert.deepEqual(reduce(state,{type:'clear'}).supplied,[]);
});

test('review refuses stale curriculum choices, keeps explanations verbatim and enforces chat limits',()=>{
  const details=confirmedDetails(answer,curricula,{'completion:Z4/L':{value:'passed',explanation:'Actually I am not sure.'},'completion:Z3/L':{value:'unknown',explanation:''}},scope);
  assert.match(followUpMessage('Question',scope,details,['completion:Z4/L']),/I have passed Z4\/L\.\nActually I am not sure\./);
  assert.throws(()=>followUpMessage('Question',{...scope,curriculumId:'other'},details,['completion:Z4/L']),/details_changed/);
  assert.throws(()=>followUpMessage('Question',scope,details,['invented']),/details_changed/);
  assert.throws(()=>followUpMessage('界'.repeat(6000),scope,details,[]),/clarification_too_long/);
});

test('retained details stay bounded and a confirmed new-message review consumes its composer draft',()=>{
  const state=reduce(createWorkspace(),{type:'remember',details:Array.from({length:40},(_,i)=>({...scope,key:'completion:Z'+i,code:'Z'+i,label:'Unknown',text:'I do not know whether I have passed Z'+i+'.'}))});
  assert.equal(state.supplied.length,32);assert.equal(state.supplied[0].code,'Z8');
  const sent=reduce({...state,draft:'New question'},{type:'submit',id:'review',text:'New question\n\nI do not know whether I have passed Z8.',clearDraft:true});
  assert.equal(sent.draft,'');assert.equal(sent.messages[0].text,'New question\n\nI do not know whether I have passed Z8.');
});
