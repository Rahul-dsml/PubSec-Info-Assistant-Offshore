import React, { useEffect } from 'react';
import useStreamingAvatar from '../streamingAvatarComponent/use-streaming-avatar'
// import StreamingAvatar from '../streamingAvatarComponent/StreamingAvatar'
import StreamingAvatar from '../streamingAvatarComponent/StreamingAvatar';
import { Button } from '../components/ui/button';


function StreamingAvatarWrapper() {
    const {
        stream,
        handleCreateNewSession,
        handleStart,
        handleCloseConnection,
        isConnectionOpen,
        handleRepeat,
        isStarted,
        isLoading,
    } = useStreamingAvatar();


   const speakAvatar = ()=>{
    handleRepeat("مرحبًا! كيف حالك؟ أتمنى لك يومًا سعيدًا ومليئًا بالنجاح")
   }


    return (
        <div>
            <div>
                <Button onClick={handleCreateNewSession} disabled={isConnectionOpen || isLoading}>
                    Create New Session
                </Button>
                <Button onClick={handleStart} disabled={isStarted || isLoading}>
                    Start Session
                </Button>
                <Button onClick={handleCloseConnection} disabled={!isConnectionOpen || isLoading}>
                    Close Connection
                </Button>
                <Button onClick={speakAvatar} disabled={!isConnectionOpen}>
                   speak
                </Button>
            </div>
            {/* Pass the stream to the StreamingAvatar component */}
            {stream ? (
                <StreamingAvatar stream={stream} />
            ) : (
                <p>No stream available. Please start a session.</p>
            )}
        </div>
    );
}

export default StreamingAvatarWrapper;
